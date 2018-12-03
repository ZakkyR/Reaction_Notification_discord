import os
import discord
import db_access
import re

client = discord.Client()

TOKEN = os.environ['DISCORD_TOKEN']

BOT_STR = 'rn!'

'''''''''''''''
Events
'''''''''''''''
# 初期登録
@client.event
async def on_server_join(server):
    try:
        if(db_access.count_server_mst(server.id) != 0):
            db_access.upsert_server_mst(server.id)

            await client.send_message(server.default_channel, 'リアクションをユーザーに通知します！\n使うには`' + BOT_STR + 'entry`と入力してください。')

    except Exception as ex:
        await client.send_message(server.default_channel, ex)

# コマンド受付
@client.event
async def on_message(message):

    command = lambda text: message.content.startswith(BOT_STR + text)

    if command('entry'):
        await entry_user(message)

    if command('del'):
        await delete_user(message)

    if message.content == 'あ！':
        await client.send_message(message.channel, 'スーモ❗️🌚ダン💥ダン💥ダン💥シャーン🎶スモ🌝スモ🌚スモ🌝スモ🌚スモ🌝スモ🌚ス〜〜〜モ⤴スモ🌚スモ🌝スモ🌚スモ🌝スモ🌚スモ🌝ス～～～モ⤵🌞')

    if message.content == '今日の性癖を貼って':
        await client.send_message(message.channel, 't!danbooru')
# リアクション時rn!
@client.event
async def on_reaction_add(reaction, user):
    message = reaction.message

    if db_access.count_user_mst(message.server.id, message.author.id) > 0:
        str_msg = [
            ('{0}が{1}:{2}のメッセージにリアクションしました!').format(user.display_name, reaction.message.server.name, reaction.message.channel.name),
            "```",
            reaction.message.content,
            "```",
            '絵文字:{0}'.format(reaction.emoji.name + '(カスタム)' if reaction.custom_emoji else reaction.emoji)
        ]
        
        await client.send_message(reaction.message.author, '\n'.join(str_msg))


'''''''''''''''
Methods
'''''''''''''''

# ユーザー登録
async def entry_user(message):
    try:
        lst_command = message.content.split(' ')
        print(lst_command)

        author = message.author
        print(message.server)

        if len(lst_command) > 3:
            raise ValueError('引数の数が違います')

        elif len(lst_command) == 2:
            try:
                user_id = lst_command[1]
                
                for c in ('<@', '>'):
                    user_id = user_id.replace(c, '')
                    
                author = await client.get_user_info(user_id)
            except:
                raise ValueError('ユーザー名に誤りがあります')
        
        if db_access.count_user_mst(message.server.id, author.id) > 0:
            error_msg = '{0} はすでに登録されています'.format(author.display_name)
            raise ValueError(error_msg)

        db_access.insert_user_mst(message.server.id, author.id)

    except Exception as ex:
        await client.send_message(message.channel, ex)
    
    else:
        success_msg = '{0} をユーザー登録しました'.format(author.display_name)
        await client.send_message(message.channel, success_msg)

# ユーザー削除
async def delete_user(message):
    try:
        lst_command = message.content.split(' ')

        author = message.author

        if len(lst_command) > 3:
            raise ValueError('引数の数が違います')

        elif len(lst_command) == 2:
            try:
                user_id = re.match('[0-9]*', lst_command[1])
                print(user_id)
                author = await client.get_user_info(user_id)
            except:
                raise ValueError('ユーザー名に誤りがあります')
        
        if db_access.count_user_mst(message.server.id, author.id) == 0:
            error_msg = '{0} は登録されていません'.format(author.display_name)
            raise ValueError(error_msg)

        db_access.delete_user_mst(message.server.id, author.id)

    except Exception as ex:
        await client.send_message(message.channel, ex)
    
    else:
        success_msg = '{0} をユーザー削除しました'.format(author.display_name)
        await client.send_message(message.channel, success_msg)

client.run(TOKEN)
