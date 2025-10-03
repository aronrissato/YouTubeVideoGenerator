import asyncio
import edge_tts
import os


def get_speech_mp3(
    texto,
    saida="music/voice.mp3",
    voz="en-US-BrianMultilingualNeural",
    velocidade="-30%",
):
    os.makedirs(os.path.dirname(saida), exist_ok=True)

    async def run():
        communicate = edge_tts.Communicate(texto, voice=voz, rate=velocidade)
        await communicate.save(saida)

    asyncio.run(run())
    return saida


if __name__ == "__main__":
    get_speech_mp3(
        """Psalm 23 thou anointest
            my head with oil; my cup runneth over.
             Surely goodness and mercy shall follow
              me all the days of my life: and I will
               dwell in the house of the Lord for ever."""
    )
