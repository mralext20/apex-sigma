import discord
from collections import deque

from sigma.plugin import Plugin
from sigma.utils import create_logger, bold

from config import permitted_id, permitted_roles
from config import permitted_roles as karaoke_override


client = discord.Client()

karaoke = False
karaoke_mod = True
karaoke_channel = 'Music Room'
karaoke_strict = False

karaoke_queue = deque()
karaoke_deban = [False, 0]


def checkPermissions(user):
    # Checking a list of permitted users
    # if user.id in permitted_id: return True
    for id in permitted_id:
        if id == user.id: return True

    # Checking a list of permitted roles
    for permitted_role in permitted_roles:
        for user_role in user.roles:
            if user_role.name == permitted_role: return True
    # if (user.id) == '125750263687413760': return True
    # for role in user.roles:
    #        if (role.name == 'Admin'): return True

    return False


def boolToStr(input):
    if input:
        return 'True'
    else:
        return 'False'


# @client.event
class VoiceChangeDetection(Plugin):
    is_global = True
    log = create_logger('voice state')

    async def on_voice_state_update(self, before, after):
        global karaoke
        global karaoke_mod
        global karaoke_channel
        global karaoke_strict
        log = True
        if karaoke_mod:
            if karaoke:
                # print("karaoke's running")
                if (after.voice.voice_channel == None) or (after.voice.voice_channel.name != karaoke_channel):
                    if after.voice.mute == True:  # if he's muted
                        if log: print('not in karaoke channel, unmuting')
                        await self.client.server_voice_state(after, mute=False)  # unmute him
                try:
                    if after.voice.voice_channel.name == karaoke_channel:
                        if karaoke_strict:
                            for role in after.roles:  # iterate through roles of a user
                                if role.name in karaoke_override:
                                    if log: print('strict, overriden, aborting')
                                    return  # if user has an override role
                            if after.voice.mute == False:  # if user is not muted
                                if log: print('strict, not overriden, muting')
                                await self.client.server_voice_state(after, mute=True)  # otherwise mute the user
                                return

                        else:
                            if after.voice.mute == True:  # if user is muted
                                if log: print('not strict, ummuting')
                                await self.client.server_voice_state(after, mute=False)  # unmute
                                return

                except AttributeError:
                    pass  # catching an exception when user disconnects from voice (switches voice channel to None)

                if (after.voice.voice_channel == None) or (after.voice.voice_channel.name != karaoke_channel):
                    if after.voice.mute == True:  # if he's muted
                        if log: print('not in karaoke channel, unmuting')
                        await self.client.server_voice_state(after, mute=False)  # unmute him


# @client.event
class Control(Plugin):
    is_global = True
    log = create_logger('Karaoke Control')

    async def on_message(self, message, pfx):
        global karaoke
        global karaoke_mod
        global karaoke_channel
        global karaoke_strict
        global karaoke_queue
        global karaoke_deban

        async def lookforstrayspotlight(server):
            for spotlight in server.roles:
                if spotlight.name == 'Karaoke Spotlight':
                    for user in server.members:  # iterating through server members
                        for role in user.roles:  # through their roles
                            if role == spotlight:  # looking of spotlight roles
                                await self.client.remove_roles(user, spotlight)  # taking it away =P

        async def assignspotlight(target):
            for role in target.server.roles:
                if role.name == 'Karaoke Spotlight':
                    await self.client.add_roles(target, role)

        async def enforcestrictmode():
            global karaoke_strict
            karaoke_strict = True
            temp = []
            for channel in message.server.channels:  # iterate through server channels
                if channel.name == karaoke_channel:  # find the karaoke channel
                    for user in channel.voice_members:  # iterate through users in the channel
                        temp.append(user)

            for user in temp:
                overridden = False
                for role in user.roles:
                    if role.name in karaoke_override:
                        overridden = True
                        break
                if not overridden:
                    await self.client.server_voice_state(user, mute=True)
                    # else: await self.client.server_voice_state(user, mute = True)
                    # for channel in message.server.channels:  # iterate through server channels
                    #    if channel.name == karaoke_channel:  # find the karaoke channel
                    #        for user in channel.voice_members:  # iterate through users in the channel
                    #            if user in karaoke_override:
                    #                return
                    #            else:
                    #                await self.client.server_voice_state(user, mute=True)  # mute them

        async def disablestrictmode():
            for channel in message.server.channels:  # iterate through server channels
                if channel.name == karaoke_channel:  # find the karaoke channel
                    for user in channel.voice_members:  # iterate through users in the channel
                        await self.client.server_voice_state(user, mute=False)  # mute them

        async def isuserinvoicechannel(target_channel, target_user):
            for channel in message.server.channels:  # iterate through server channels
                if channel.name == target_channel:  # find the karaoke channel
                    for user in channel.voice_members:  # iterate through users in the channel
                        if user.id == target_user.id:  # user is in the channel
                            return True
            return False

        async def mutekaraokechannel():
            temp = []
            for channel in message.server.channels:  # iterate through server channels
                if channel.name == karaoke_channel:  # find the karaoke channel
                    for user in channel.voice_members:  # iterate through users in the channel
                        temp.append(user)
            for user in temp:
                await self.client.server_voice_state(user, mute=True)  # unmute them

        async def unmutekaraokechannel():
            temp = []
            for channel in message.server.channels:  # iterate through server channels
                if channel.name == karaoke_channel:  # find the karaoke channel
                    for user in channel.voice_members:  # iterate through users in the channel
                        temp.append(user)
            for user in temp:
                await self.client.server_voice_state(user, mute=False)  # unmute them

        if message.content.startswith(pfx + 'startkaraoke'):
            if checkPermissions(message.author):
                if karaoke_mod:
                    karaoke_mod = False
                    await self.client.send_message(message.channel, "Karaoke mode is set to false, not muting users")
                else:
                    karaoke_mod = True
                    await self.client.send_message(message.channel, "Karaoke mode is set to true, muting users")
            else:
                await self.client.send_message(message.channel, "Insufficient permissions")

        elif message.content.startswith(pfx + 'startkaraoke'):
            if checkPermissions(message.author):
                target = message.content[len(pfx) + len('startkaraoke') + 1:]
                if (len(target)) == 0:
                    await self.client.send_message(message.channel, "No channel specified, aborting")
                    return

                global karaoke, karaoke_channel, karaoke_strict
                try:
                    karaoke = True
                    karaoke_channel = target
                    # karaoke_strict = True
                    # try:
                    await lookforstrayspotlight(message.server)
                    await enforcestrictmode()
                    await self.client.send_message(message.channel,
                                                   "Karaoke started in strict mode on channel " + karaoke_channel)

                except SyntaxError:
                    await self.client.send_message(message.channel, "Error while starting karaoke session")
            else:
                await self.client.send_message(message.channel, "Insufficient permissions")

        elif message.content.startswith(pfx + 'stopkaraoke'):
            if checkPermissions(message.author):
                if karaoke:
                    karaoke = False
                    temp = []
                    for channel in message.server.channels:  # iterate through server channels
                        if channel.name == karaoke_channel:  # find the karaoke channel
                            for user in channel.voice_members:  # iterate through users in the channel
                                temp.append(user)
                            break
                    for user in temp: await self.client.server_voice_state(user, mute=False)  # unmute them
                    await self.client.send_message(message.channel, "Karaoke stopped")
                else:
                    await self.client.send_message(message.channel, "No ongoing karaoke found")
            else:
                await self.client.send_message(message.channel, "Insufficient permissions")

        elif message.content.startswith(pfx + 'karaokestrict'):
            if checkPermissions(message.author):

                if karaoke_strict:
                    karaoke_strict = False
                    await unmutekaraokechannel()
                    # for channel in message.server.channels:  # iterate through server channels
                    #    if channel.name == karaoke_channel:  # find the karaoke channel
                    #        for user in channel.voice_members:  # iterate through users in the channel
                    #            await self.client.server_voice_state(user, mute=False)  # unmute them
                    await self.client.send_message(message.channel, "Strict mode disabled")
                else:
                    await enforcestrictmode()
                    # karaoke_strict = True
                    # for channel in message.server.channels:  # iterate through server channels
                    #    if channel.name == karaoke_channel:  # find the karaoke channel
                    #        for user in channel.voice_members:  # iterate through users in the channel
                    #            for role in user.roles:  # iterate through roles of a user
                    #                if role in karaoke_override:
                    #                    return
                    #                else:
                    #                    await self.client.server_voice_state(user, mute=True)  # mute them
                    await self.client.send_message(message.channel, "Strict mode enabled")
            else:
                await self.client.send_message(message.channel, "Insufficient permissions")

        elif message.content.startswith(pfx + 'handup'):
            await self.client.send_typing(message.channel)
            if karaoke:
                if not message.author.id in karaoke_queue:
                    karaoke_queue.append(message.author)
                    await self.client.send_message(message.channel,
                                                   '<@' + message.author.id + '> has joined the singers list!\nA round of applause please! :musical_note: :clap:')
                else:
                    await self.client.send_message(message.channel,
                                                   'I\'m sorry <@' + message.author.id + '>, but you\'re already on the list...')
            else:
                await self.client.send_message(message.channel, 'No karaoke session running')

        elif message.content.startswith(pfx + 'repertoire'):
            if karaoke:
                await self.client.send_typing(message.channel)
                if len(karaoke_queue) != 0:
                    singer_list = ''
                    n = 1
                    for user in karaoke_queue:
                        singer_list += '\n#' + str(n) + ': <@' + str(user.id) + '>'
                        n += 1
                    await self.client.send_message(message.channel, singer_list)
                else:
                    await self.client.send_message(message.channel, 'The list seems to be empty')
            else:
                await self.client.send_message(message.channel, 'No karaoke session running')

        elif message.content.startswith(pfx + 'clearqueue'):
            if checkPermissions(message.author):
                karaoke_queue.clear()
                await self.client.send_message(message.channel, 'Karaoke queue cleared')
            else:
                await self.client.send_message(message.channel, "Insufficient permissions")

        elif message.content.startswith(pfx + 'karaokeremove'):
            if checkPermissions(message.author):
                target = message.content[len(pfx) + len('karaokeremove') + 1:]
                if (len(target)) == 0:
                    await self.client.send_message(message.channel, "No user specified, aborting")
                    return
                if message.mentions[0] in karaoke_queue:
                    karaoke_queue.remove(message.mentions[0])
                    await self.client.send_message(message.channel, 'User removed from the queue')
                else:
                    await self.client.send_message(message.channel, 'User not found in the queue')
            else:
                await self.client.send_message(message.channel, "Insufficient permissions")

        elif message.content.startswith(pfx + 'handdown'):
            if karaoke:
                if message.author in karaoke_queue:
                    karaoke_queue.remove(message.author)
                    await self.client.send_message(message.channel,
                                                   'You have been removed from the list!\nWe\'re sorry to see you go, <@' + message.author.id + '>... :cry:')
                else:
                    await self.client.send_message(message.channel, 'I can\'t find you on the list...')
            else:
                await self.client.send_message(message.channel, 'No karaoke session running')

        elif message.content.startswith(pfx + 'takemic'):
            if not karaoke_deban[0]:  # if its not someone's else turn
                if message.author in karaoke_queue:  # if user is in the queue
                    if message.author == karaoke_queue[0]:  # if its his/her turn
                        he_is = await isuserinvoicechannel(karaoke_channel, karaoke_queue[0])
                        if he_is:
                            karaoke_deban = [True, karaoke_queue.popleft()]

                            await lookforstrayspotlight(message.server)
                            await assignspotlight(karaoke_deban[1])
                            await self.client.send_message(message.channel,
                                                           '<@' + karaoke_deban[
                                                               1].id + '> is morally ready, enforcing strict mode')
                            await enforcestrictmode()
                            await self.client.server_voice_state(karaoke_deban[1], mute=False)
                            return
                        else:
                            self.client.send_message(message.channel,
                                                     '<@' + karaoke_queue[0].id + "> you're not in karaoke channel")
                    else:
                        await self.client.send_message(message.channel,
                                                       "<@" + message.author.id + "> it's not your turn yet")
                else:
                    await self.client.send_message(message.channel,
                                                   "<@" + message.author.id + "> you're not in the queue")
            else:
                self.client.send_message(message.channel, "Shh, it's <@" + karaoke_deban[1].id + "> singing time")

        elif message.content.startswith(pfx + 'dropmic'):
            # try:
            if karaoke_deban[0]:
                if message.author == karaoke_deban[1]:
                    karaoke_strict = False
                    await unmutekaraokechannel()
                    # for channel in message.server.channels:  # iterate through server channels
                    #    if channel.name == karaoke_channel:  # find the karaoke channel
                    #        for user in channel.voice_members:
                    #            await self.client.server_voice_state(user, mute=False)  # unmute them
                    await self.client.send_message(message.channel,
                                                   'It seems <@' + karaoke_deban[
                                                       1].id + '> is done, unfortunatelly at the cost of a broken microphone!\nWe broudght spares, yay~! Whenever the next singer is ready, type ' + bold(
                                                       pfx) + bold('takemic') + '!')
                    karaoke_deban = [False, 0]
                    return
                else:
                    print('1')
                    await self.client.send_message(message.channel,
                                                   "What do you think you're dropping <@" + message.author.id + "> ?")
            else:
                print('2')
                await self.client.send_message(message.channel,
                                               "What do you think you're dropping <@" + message.author.id + "> ?")
                # except TypeError:
                #    print('3')
                #    await self.client.send_message(message.channel, "What do you think you're dropping <@" + message.author.id + "> ?")


        elif message.content.startswith(pfx + 'karaokestatus'):
            out = 'Karaoke mode ' + bold(boolToStr(karaoke_mod)) + '\n'
            out += 'Session ongoing ' + bold(boolToStr(karaoke)) + '\n'
            out += 'Channel ' + bold(karaoke_channel) + '\n'
            out += 'Strict mode ' + bold(boolToStr(karaoke_strict))

            await self.client.send_message(message.channel, out)


        elif message.content.startswith(pfx + 'forceunmute'):
            if checkPermissions(message.author):
                print('Force unmuting')
                # temp = []
                # for channel in message.server.channels:  # iterate through server channels
                #    if channel.name == karaoke_channel:  # find the karaoke channel
                #        for user in channel.voice_members:  # iterate through users in the channel
                #            temp.append(user)
                # for user in temp:
                #    await self.client.server_voice_state(user, mute=False)  # unmute them

                await unmutekaraokechannel()
                await self.client.send_message(message.channel, "Iterated through channel")
                print()

        elif message.content.startswith(pfx + 'forcemute'):
            if checkPermissions(message.author):
                print('Force muting')
                # temp = []
                # for channel in message.server.channels:  # iterate through server channels
                #    if channel.name == karaoke_channel:  # find the karaoke channel
                #        for user in channel.voice_members:  # iterate through users in the channel
                #            #print(user.name)
                #            temp.append(user)
                # for user in temp:
                #    print(user.name)
                #    await self.client.server_voice_state(user, mute=True)  # unmute them
                await mutekaraokechannel()
                await self.client.send_message(message.channel, "Iterated through channel")
                print()

        elif message.content.startswith(pfx + 'listchannelmembers'):
            if checkPermissions(message.author):
                for channel in message.server.channels:  # iterate through server channels
                    if channel.name == karaoke_channel:  # find the karaoke channel
                        for user in channel.voice_members:  # iterate through users in the channel
                            print(user.name)
                            # await self.client.server_voice_state(user, mute=False)  # unmute them
                            # await self.client.send_message(message.channel, "Iterated through channel")

        elif message.content.startswith(pfx + 'setchannel'):
            if checkPermissions(message.author):
                karaoke_channel = message.content[len(pfx) + len('setchannel') + 1:]
                await self.client.send_message(message.channel, "Channel set")

        elif message.content.startswith(pfx + 'signup'):
            cmd_name = 'karaoke signup'
            await self.client.send_typing(message.channel)
            try:
                self.log.info(
                    'User %s [%s] on server %s [%s], used the ' + cmd_name + ' command on #%s channel',
                    message.author,
                    message.author.id, message.server.name, message.server.id, message.channel)
            except:
                self.log.info('User %s [%s], used the ' + cmd_name + ' command.',
                              message.author,
                              message.author.id)

            query = "SELECT EXISTS (SELECT USER_ID FROM KARAOKE_LIST WHERE USER_ID=?);"
            info_grabber_checker = self.db.execute(query, str(message.author.id))

            for info_check in info_grabber_checker:
                if info_check[0] == 0:

                    query = 'INSERT INTO KARAOKE_LIST (USER_ID, USER_NAME) VALUES (?, ?)'
                    self.db.execute(query, str(message.author.id), str(message.author.name))
                    self.db.commit()

                    await self.client.send_message(message.channel, 'Thank you for signing up for the Karaoke event, <@' + message.author.id + '>!')
                else:
                    await self.client.send_message(message.channel, 'It seems you\'ve already signed up, <@' + message.author.id + '>!')
        elif message.content.startswith(pfx + 'karaokelist'):
            cmd_name = 'karaoke signup sheet list'
            await self.client.send_typing(message.channel)

            try:
                self.log.info(
                    'User %s [%s] on server %s [%s], used the ' + cmd_name + ' command on #%s channel',
                    message.author,
                    message.author.id, message.server.name, message.server.id, message.channel)
            except:
                self.log.info('User %s [%s], used the ' + cmd_name + ' command.',
                              message.author,
                              message.author.id)

            query = 'SELECT USER_NAME FROM KARAOKE_LIST'
            username_grabber = self.db.execute(query)

            out_text = ''
            n = 0
            for username in username_grabber:
                n += 1
                out_text += '\n#' + str(n) + ' [ ' + str(username[0]) + ' ]'
            if out_text == '':
                await self.client.send_message(message.channel, 'Nobody signed up yet...')
            else:
                await self.client.send_message(message.channel, out_text)



                # elif message.content.startswith(pfx + 'karaokestrict'):
                #   if karaoke_strict:
                #       karaoke_strict = False
                #       for channel in message.server.channels: #iterate through server channels
                #           if channel.name == karaoke_channel: #find the karaoke channel
                #               for user in channel.voice_members: #iterate through users in the channel
                #                   await self.client.server_voice_state(user, mute=False) #unmute them
                #       await self.client.send_message(message.channel, "Strict mode disabled")
                #   else:
                #       karaoke_strict = True
                #       for channel in message.server.channels: #iterate through server channels
                #           if channel.name == karaoke_channel: #find the karaoke channel
                #               for user in channel.voice_members: #iterate through users in the channel
                #                   await self.client.server_voice_state(user, mute=True) #mute them
                #       await self.client.send_message(message.channel, "Strict mode enabled")

                # elif message.content.startswith(pfx + 'karaoke'):
                #    await self.client.send_typing(message.channel)
                #    cmd_name = 'Repertiore'
                #    dbsql = sqlite3.connect('storage/server_settings.sqlite', timeout=20)
                #    #self.log.info('\nUser %s [%s] on server %s [%s], used the ' + cmd_name + ' command on #%s channel',
                #    #              message.author,
                #    #              message.author.id, message.server.name, message.server.id, message.channel)
                #    await self.client.send_message(message.channel,
                #                                   '```css\n[' + pfx + cmd_handup + '] Adds you to the singers list.' +
                #                                   '\n[' + pfx + cmd_handdown + '] Removes you to the singers list.' +
                #                                   '\n[' + pfx + cmd_repertoire + '] Lists the current singers.' +
                #                                   '\n[' + pfx + cmd_takemic + '] Mutes everyone except you so you can start.' +
                #                                   '\n[' + pfx + cmd_dropmic + '] Unmutes everyone and marks your performance as done.' +
                #                                   '\n[' + pfx + 'karaoke' + '] Lists these commands.' +
                #                                   '\n```')
