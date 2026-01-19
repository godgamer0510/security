import discord
from discord.ext import commands

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # 永続的なView

    @discord.ui.button(label="認証する (Verify)", style=discord.ButtonStyle.green, custom_id="verify_button")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 「Verified」ロールを付与 (ロール名はサーバーに合わせてください)
        role = discord.utils.get(interaction.guild.roles, name="Member")
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("認証が完了しました！", ephemeral=True)
        else:
            await interaction.response.send_message("エラー: 'Member' ロールが見つかりません。", ephemeral=True)

class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        # Bot再起動時にもボタンが動作するようにViewを登録
        self.bot.add_view(VerifyView())

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup_verify(self, ctx):
        """認証パネルを設置するコマンド"""
        embed = discord.Embed(title="セキュリティ認証", description="下のボタンを押してサーバーへのアクセス権を取得してください。")
        await ctx.send(embed=embed, view=VerifyView())

async def setup(bot):
    await bot.add_cog(Verify(bot))