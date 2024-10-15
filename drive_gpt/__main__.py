import asyncio
import enum
import json
from typing import Optional
from PIL import ImageGrab
import base64
import io
from openai import BaseModel, OpenAI


OPENAI_API_KEY = "<your-openai-api-key>"


class SelfDrivingAction(enum.Enum):
    GAS = "GAS"
    BRAKE = "BRAKE"
    TURN_LEFT = "TURN_LEFT"
    TURN_RIGHT = "TURN_RIGHT"


class SelfDrivingActionModel(BaseModel):
    action: Optional[SelfDrivingAction]
    

class SelfDrivingCar:
    def __init__(self, oai_client: OpenAI):
        self.client = oai_client

    async def _run(self):
        while True:
            image = await self._take_picture()

            what_to_do = await self._determine_what_to_do(image)
            assert what_to_do in SelfDrivingAction.__members__
            print(what_to_do)
            
            await asyncio.sleep(3)

    async def _take_picture(self):
        image = ImageGrab.grab()
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    async def _determine_what_to_do(self, image) -> SelfDrivingAction:
        response = self.client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this image and determine the appropriate driving action. Respond with a JSON object with the key 'action' and a value of one of these values (NOTHING ELSE): GO, BRAKE, TURN_LEFT, or TURN_RIGHT."},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image}"}}
                    ],
                }
            ],
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        response_str = response.choices[0].message.content
        response_json = json.loads(response_str)
        return response_json["action"]

    async def start(self):
        asyncio.create_task(self._run())


if __name__ == "__main__":
    client = OpenAI(api_key=OPENAI_API_KEY)
    car = SelfDrivingCar(client)
    asyncio.run(car.start())
