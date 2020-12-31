from discord.ext import commands
from discord.ext.commands import Cog
from bot.bot import Bot
import requests
from discord import Embed
from .eval import GREEN
import os

PREFIX = os.getenv('PREFIX')

class GitHub(Cog):
	def __init__(self, bot:Bot):
		self.bot = bot

	@commands.command(help='Get the top 5 contributors of the bot.')
	async def contributors(self, ctx):
		response = requests.get('https://api.github.com/repos/gurkult/gurkbot/contributors').json()[-5:]
		em = Embed(title = 'Awesome People Who have contributed to this Bot!', color=GREEN)
		em.set_thumbnail(url='https://avatars3.githubusercontent.com/u/72938830?s=200&v=4')
		for contributor in response:
			em.add_field(name=contributor['login'], value='{} commits\n[Profile](https://github.com/{})'.format(contributor['contributions'], contributor['login']))
		em.add_field(name='You Can Contribute Too!', value="Here's our [GitHub Repo](https://github.com/gurkult/gurkbot)")
		await ctx.send(embed=em)

	@commands.command(help=f'{PREFIX}gitsearch users <username> to search users and {PREFIX}gitsearch repos <reponame> to search repos.')
	async def gitsearch(self, ctx, what,*,term):
		if what.lower() == 'users':
			response = requests.get(f'https://api.github.com/search/users?q={term}').json()
			results_count = response['total_count']
			if results_count == 0:
				await ctx.send('No Results Found.')
			else:
				# here ************* here ************ here*************
				results_embed = Embed(title=f'{results_count} results for {term}', color=GREEN)
				results_embed.set_thumbnail(url='https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png')
				if len(response['items']) > 3:
					for user in response['items'][-10:]:
						profile_link = user['html_url']
						results_embed.add_field(name=user['login'], value=profile_link, inline=False)

					await ctx.send(embed=results_embed)
				elif len(response['items']) <= 3:
					absolute_result = response['items'][0]
					absolute_result_embed = Embed(title=absolute_result['login'], color=GREEN)
					absolute_result_embed.set_thumbnail(url=absolute_result['avatar_url'])
					absolute_result_embed.add_field(name='Profile', value=absolute_result['html_url'])
					await ctx.send(embed=absolute_result_embed)

		elif what.lower() == 'repos':
			response = requests.get(f'https://api.github.com/search/repositories?q={term}').json()
			results_count = response['total_count']
			if results_count == 0:
				await ctx.send('No results found.')
			else:
				results_embed = Embed(title=f'{results_count} Results for {term}', color=GREEN)
				results_embed.set_thumbnail(url='https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png')

				if len(response['items']) > 3:
					for result in response['items'][-10:]:
						repo_link = result['html_url']
						results_embed.add_field(name=result['full_name'], value=f'{repo_link}', inline=False)
					await ctx.send(embed = results_embed)
				elif len(response['items']) <= 3:
					absolute_result = response['items'][0]
					absolute_result_link = absolute_result['html_url']
					absolute_result_embed = Embed(title=absolute_result['full_name'], color=GREEN)
					absolute_result_embed.set_thumbnail(url=absolute_result['owner']['avatar_url'])
					absolute_result_embed.add_field(name='Description', value=absolute_result['description'], inline=False)
					absolute_result_embed.add_field(name='Most Used Language', value=absolute_result['language'], inline=False)
					absolute_result_embed.add_field(name='Forks', value=absolute_result['forks_count'], inline=False)
					absolute_result_embed.add_field(name='Repository', value=absolute_result_link, inline=True)
					await ctx.send(embed=absolute_result_embed)

		else:
			await ctx.send(f'Command syntax:\nFor Users\n`{PREFIX}gitsearch users username`\n\nFor Repositories\n`{PREFIX}gitsearch repos reponame`')


def setup(bot):
	bot.add_cog(GitHub(bot))