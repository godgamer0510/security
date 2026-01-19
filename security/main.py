import discord
import os
import aiosqlite
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# Intentの設定（これがないとメンバー検知やメッセージ内容が見れません）
intents = discord.Intents.all()

class SecurityBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.db_path = "/data/security.db" # Railwayのボリュームパス

    async def setup_hook(self):
        # DB初期化
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    guild_id INTEGER,
                    channel_id INTEGER
                )
            """)
            await db.commit()
        
        # Cogsの読み込み
        await self.load_extension("cogs.security")
        await self.load_extension("cogs.verify")
        print("Cogs loaded.")

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')

bot = SecurityBot()

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))