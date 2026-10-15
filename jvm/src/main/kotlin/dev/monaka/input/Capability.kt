package dev.monaka.input

/** Generated from schema/capabilities.json. */
enum class Capability(val token: String) {
    POSITION("position"),
    ORIENTATION("orientation"),
    LINEAR_VELOCITY("linear_velocity"),
    ANGULAR_VELOCITY("angular_velocity"),
    LINEAR_ACCELERATION("linear_acceleration"),
    BATTERY_FRACTION("battery_fraction"),
    CHARGING("charging");
    companion object { fun parse(token: String): Capability = entries.firstOrNull { it.token == token } ?: throw ContractError("UnsupportedValue") }
}
