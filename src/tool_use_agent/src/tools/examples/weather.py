"""
Weather tool example (simulated)
"""
from typing import Dict, Any
import random
from ..base import BaseTool, ToolResult, ToolParameter


class WeatherTool(BaseTool):
    """Simulated weather tool"""

    def __init__(self):
        """Initialize weather tool"""
        super().__init__()
        self._parameters = {
            "location": ToolParameter(
                name="location",
                type="string",
                description="City name or location",
                required=True
            )
        }

    @property
    def name(self) -> str:
        """Tool name"""
        return "weather"

    @property
    def description(self) -> str:
        """Tool description"""
        return "Get current weather information for a location"

    async def execute(self, location: str) -> ToolResult:
        """
        Get weather for location (simulated)

        Args:
            location: Location name

        Returns:
            ToolResult: Weather information
        """
        # Simulate weather data
        weather_conditions = ["sunny", "cloudy", "rainy", "snowy", "partly cloudy"]
        temp = random.randint(-5, 35)
        humidity = random.randint(30, 90)
        wind_speed = random.randint(0, 30)
        condition = random.choice(weather_conditions)

        return ToolResult(
            success=True,
            data={
                "location": location,
                "temperature": temp,
                "humidity": humidity,
                "wind_speed": wind_speed,
                "condition": condition,
                "units": "celsius"
            },
            metadata={"source": "simulated"}
        )