import discord
from discord.ext import commands
import re
import datetime
from collections import deque, defaultdict

class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # アンチレイド用: 参加時間を記録 (過去10秒間の参加者を保持)
        self.join_queue = deque(maxlen=10) 
        # アンチスパム用: ユーザーごとのメッセージ履歴
        self.spam_check = defaultdict(lambda: deque(maxlen=5))
        
        # 危険なドメインの簡易リスト (実運用では外部API推奨)
        self.banned_domains = ["discord-nitro-free.com", "steam-gift-promo.xyz"]

    # --- アンチレイド (Anti-Raid) ---
    @commands.Cog.listener()
    async def on_member_join(self, member):
        now = datetime.datetime.now().timestamp()
        self.join_queue.append(now)

        # 10秒以内に5人以上参加したらレイドと判定
        if len(self.join_queue) >= 5:
            delta = self.join_queue[-1] - self.join_queue[0]
            if delta < 10: 
                # レイド検知時の処理: サーバー参加制限や通知
                # ここでは簡易的にログ出力のみ
                print(f"🚨 RAID DETECTED in {member.guild.name}!")
                # 実装案: await member.guild.edit(verification_level=discord.VerificationLevel.high)

    # --- メッセージ監視 (スパム & リンク) ---
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # 1. リンクフィルター
        urls = re.findall(r'https?://[^\s]+', message.content)
        for url in urls:
            if any(domain in url for domain in self.banned_domains):
                await message.delete()
                await message.channel.send(f"{message.author.mention} ⚠️ 危険なリンクを検知しました。", delete_after=5)
                return

        # 2. アンチスパム (連投検知)
        user_history = self.spam_check[message.author.id]
        user_history.append({
            'content': message.content,
            'time': message.created_at.timestamp()
        })

        if len(user_history) == 5:
            # 5通のメッセージが5秒以内に送信された場合
            if user_history[-1]['time'] - user_history[0]['time'] < 5:
                await message.delete()
                await message.channel.send(f"{message.author.mention} ⚠️ メッセージ送信が速すぎます！(タイムアウト処理などをここに実装)", delete_after=3)
                # 実装案: await message.author.timeout(...)
            
            # 同じ内容の連続送信チェック
            if all(msg['content'] == user_history[0]['content'] for msg in user_history):
                await message.delete()
                await message.channel.send(f"{message.author.mention} ⚠️ 同じ内容を連投しないでください。", delete_after=3)

    # --- 詳細な監査ログ (Advanced Logging) ---
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot: return
        
        # ログ送信先のチャンネルを取得 (DBなどから取得するのが理想)
        # ここでは仮に 'security-logs' という名前のチャンネルを探して送信
        log_channel = discord.utils.get(message.guild.channels, name="security-logs")
        if log_channel:
            embed = discord.Embed(title="🗑️ Message Deleted", color=discord.Color.red())
            embed.add_field(name="Author", value=message.author.mention, inline=True)
            embed.add_field(name="Channel", value=message.channel.mention, inline=True)
            embed.add_field(name="Content", value=message.content or "画像のみなど", inline=False)
            embed.timestamp = datetime.datetime.now()
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content: return

        log_channel = discord.utils.get(before.guild.channels, name="security-logs")
        if log_channel:
            embed = discord.Embed(title="✏️ Message Edited", color=discord.Color.orange())
            embed.add_field(name="Author", value=before.author.mention)
            embed.add_field(name="Channel", value=before.channel.mention)
            embed.add_field(name="Before", value=before.content, inline=False)
            embed.add_field(name="After", value=after.content, inline=False)
            await log_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Security(bot))