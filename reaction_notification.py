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
async def on_message(message:discord.Message):

    if not message.author.bot:

        command = lambda text: message.content.startswith(BOT_STR + text)

        try:
            if command('entry'):
                await entry_user(message)

            elif command('del'):
                await delete_user(message)

            elif command('sc_add'):
                await regist_message(message)

            elif command('sc_del'):
                await delete_message(message)

            elif command('sc_list'):
                await get_shortcut_list(message)

            else:
                # ショートカット
                await get_message(message)

        except Exception as ex:
            await client.send_message(message.channel, ex)

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
async def entry_user(message:discord.Message):

    lst_command = message.content.split(' ')
    print(lst_command)

    author = message.author
    print(message.server)

    if len(lst_command) > 3:
        raise ValueError('引数の数が違います')

    elif len(lst_command) == 2:
        try:
            user_id = lst_command[1]
            
            for c in ('<@', '>', '!'):
                user_id = user_id.replace(c, '')
                
            author = await client.get_user_info(user_id)
        except:
            raise ValueError('ユーザー名に誤りがあります')
    
    if db_access.count_user_mst(message.server.id, author.id) > 0:
        error_msg = '{0} はすでに登録されています'.format(author.display_name)
        raise ValueError(error_msg)

    db_access.insert_user_mst(message.server.id, author.id)
    
    success_msg = '{0} をユーザー登録しました'.format(author.display_name)
    await client.send_message(message.channel, success_msg)

# ユーザー削除
async def delete_user(message:discord.Message):
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

    success_msg = '{0} をユーザー削除しました'.format(author.display_name)
    await client.send_message(message.channel, success_msg)

# メッセージショートカット登録
async def regist_message(message:discord.Message):

    lst_command = message.content.split(' ')

    if len(lst_command) != 3:
        raise ValueError('引数の数が違います')

    try:
        if db_access.get_shortcut_message(message.server.id, lst_command[1].strip()) != None:
            raise ValueError('ショートカット：`{0}`はすでに登録されています'.format(lst_command[1].strip()))

        sc_message = await client.get_message(message.channel, lst_command[2].strip())
        db_access.insert_shortcut(message.server.id, lst_command[1].strip(), sc_message.content)

        success_msg = [
            "メッセージを登録しました",
            "ショートカット：`{0}`".format(lst_command[1].strip()),
            "メッセージ：",
            "```",
            sc_message.content,
            "```",
        ]
        
        await client.send_message(message.channel, '\n'.join(success_msg))
        
    except discord.NotFound:
        raise ValueError('メッセージIDが間違っています')

# メッセージショートカット削除
async def delete_message(message:discord.Message):

    lst_command = message.content.split(' ')

    if len(lst_command) != 2:
        raise ValueError('引数の数が違います')

    if db_access.get_shortcut_message(message.server.id, lst_command[1].strip()) == None:
        raise ValueError('ショートカット：`{0}`は存在しません'.format(lst_command[1].strip()))

    db_access.delete_shortcut(message.server.id, lst_command[1].strip())

    success_msg = 'ショートカット：`{0}` を削除しました'.format(lst_command[1].strip())
    await client.send_message(message.channel, success_msg)

# メッセージショートカット出力
async def get_message(message:discord.Message):

    lst_command = message.content.split(' ')

    msg = db_access.get_shortcut_message(message.server.id, lst_command[0])

    if msg != None:
        if len(lst_command) == 1 and message.content == lst_command[0]:
            await client.send_message(message.channel, msg)

        elif len(lst_command) == 2:
            try:
                user_id = lst_command[1]

                for c in ('<@', '>', '!'):
                    user_id = user_id.replace(c, '')

                send_user = await client.get_user_info(user_id)
                await client.send_message(send_user, msg)

            except:
                pass

# メッセージショートカットリスト
async def get_shortcut_list(message:discord.Message):
    rows = db_access.get_shortcut_list(message.server.id)
    sc_list = []

    for row in rows:
        sc_list.append("`{0}`".format(row[0]))

    if len(sc_list) == 0:
        raise ValueError('ショートカットは登録されていません')

    else:
        await client.send_message(message.channel, '\n'.join(sc_list))

client.run(TOKEN)
