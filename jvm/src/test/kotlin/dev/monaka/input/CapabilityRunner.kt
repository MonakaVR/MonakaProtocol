package dev.monaka.input

import com.google.gson.GsonBuilder
import com.google.gson.JsonParser
import dev.monaka.protocol.v2.*
import java.io.File

object CapabilityRunner {
    @JvmStatic fun main(args: Array<String>) {
        try {
            if (args[0] == "--self-test") {
                check(CapabilitySet(listOf("position", "orientation")) == CapabilitySet(listOf("orientation", "position")))
                check(CapabilitySet(emptyList()).values.isEmpty())
                for (tokens in listOf(listOf("unknown"), listOf("position", "position"))) {
                    check(runCatching { CapabilitySet(tokens) }.exceptionOrNull() is ContractError)
                }
                println("PASS vocabulary/set/unknown/duplicate"); return
            }
            val d = MonakaCodec.decodeEnvelope(File(args[0]).readBytes())
            if (d is DecodeResult.Failure) { println("ERROR:${d.code}"); return }
            val message = (d as DecodeResult.Success).value
            val p = CapabilityContract.project(message)
            val encoded = MonakaCodec.encodeEnvelope(message) as EncodeResult.Success
            val channels = p.channels.mapKeys { it.key.token }.mapValues { (_, c) ->
                mapOf("supported" to c.supported, "sample_present" to c.sample_present, "valid" to c.valid, "state" to c.state)
            }
            println(GsonBuilder().serializeNulls().create().toJson(mapOf("channels" to channels, "wire" to JsonParser.parseString(encoded.value.toString(Charsets.UTF_8)))))
        } catch (e: ContractError) { println("ERROR:${e.code}") }
    }
}
