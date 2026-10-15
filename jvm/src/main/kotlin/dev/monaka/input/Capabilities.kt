package dev.monaka.input

import dev.monaka.protocol.v2.*
import java.util.Collections

class ContractError(val code: String) : IllegalArgumentException(code)

class CapabilitySet(tokens: List<String>) {
    val values: Set<Capability>
    init {
        val parsed = tokens.map(Capability::parse)
        if (parsed.size != parsed.toSet().size) throw ContractError("InconsistentValidity")
        values = Collections.unmodifiableSet(LinkedHashSet(parsed))
    }
    fun tokens(): List<String> = Capability.entries.filter { it in values }.map { it.token }
    fun subsetOf(other: CapabilitySet) = other.values.containsAll(values)
    override fun equals(other: Any?) = other is CapabilitySet && values == other.values
    override fun hashCode() = values.hashCode()
}

data class Channel(val supported: Boolean, val sample_present: Boolean, val valid: Boolean) {
    val state get() = when { !supported -> "UNSUPPORTED"; !sample_present -> "ABSENT"; valid -> "VALID"; else -> "INVALID" }
}
data class Identity(val family: String, val publisher: String, val source: String, val entity: String)
data class Projection(val identity: Identity, val session: String, val clock: String,
    val space: CoordinateSpace, val capabilities: CapabilitySet, val channels: Map<Capability, Channel>)

object CapabilityContract {
    fun project(message: Envelope): Projection {
        val checked = MonakaCodec.encodeEnvelope(message)
        if (checked is EncodeResult.Failure) throw ContractError(checked.code.name)
        val fields = when (message) {
            is TrackerObservation -> Fields(Identity("monaka.observation", "", message.source_id, message.device_id),
                message.session_id, message.clock_id, message.coordinate_space, message.capabilities, message.battery,
                message.position != null, message.orientation != null, message.validity.position, message.validity.orientation,
                message.linear_velocity != null, message.angular_velocity != null, message.linear_acceleration != null)
            is ObservationDeviceState -> Fields(Identity("monaka.observation", "", message.source_id, message.device_id),
                message.session_id, message.clock_id, message.coordinate_space, message.capabilities, message.battery)
            is MtpPose -> Fields(Identity("monaka.tracking", message.publisher_id, message.source_id, message.tracker_id),
                message.session_id, message.clock_id, message.coordinate_space, message.capabilities, null,
                message.position != null, message.orientation != null, message.validity.position, message.validity.orientation,
                message.linear_velocity != null, message.angular_velocity != null, message.linear_acceleration != null)
            is MtpTrackerState -> Fields(Identity("monaka.tracking", message.publisher_id, message.source_id, message.tracker_id),
                message.session_id, message.clock_id, message.coordinate_space, message.capabilities, message.battery)
            else -> throw ContractError("UnsupportedMessage")
        }
        val caps = CapabilitySet(fields.tokens)
        val present = listOf(fields.p, fields.q, fields.v, fields.w, fields.a,
            fields.battery?.fraction != null, fields.battery?.charging != null)
        val valid = listOf(fields.pv, fields.qv, fields.v && fields.pv, fields.w && fields.qv, fields.a && fields.pv, present[5], present[6])
        val channels = Capability.entries.associateWith { c ->
            Channel(c in caps.values, present[c.ordinal], c in caps.values && valid[c.ordinal])
        }
        return Projection(fields.id, fields.session, fields.clock, fields.space, caps, Collections.unmodifiableMap(channels))
    }
    fun withCapabilities(message: Envelope, declaration: CapabilitySet): Envelope = when (message) {
        is TrackerObservation -> message.copy(capabilities = declaration.tokens())
        is ObservationDeviceState -> message.copy(capabilities = declaration.tokens())
        is MtpPose -> message.copy(capabilities = declaration.tokens())
        is MtpTrackerState -> message.copy(capabilities = declaration.tokens())
        else -> throw ContractError("UnsupportedMessage")
    }
    fun checkBinding(value: Projection, identity: Identity, session: String, declaration: CapabilitySet) {
        if (value.identity != identity) throw ContractError("IdentityMismatch")
        if (value.session != session) throw ContractError("SessionMismatch")
        if (value.capabilities != declaration) throw ContractError("CapabilitiesChanged")
    }
    private data class Fields(val id: Identity, val session: String, val clock: String,
        val space: CoordinateSpace, val tokens: List<String>, val battery: Battery?,
        val p: Boolean = false, val q: Boolean = false, val pv: Boolean = false, val qv: Boolean = false,
        val v: Boolean = false, val w: Boolean = false, val a: Boolean = false)
}
