import os
import requests
import nhentai as nh
from PIL import Image
from io import BytesIO

from sigma.plugin import Plugin
from sigma.utils import create_logger
from sigma.database import DatabaseError


class NHentai(Plugin):
    is_global = True
    log = create_logger('nHentai')

    async def on_message(self, message, pfx):
        if message.content.startswith(pfx + 'nhentai'):
            await self.client.send_typing(message.channel)
            cmd_name = 'NHentai'

            try:
                self.log.info('User %s [%s] on server %s [%s], used the ' + cmd_name + ' command on #%s channel',
                              message.author,
                              message.author.id, message.server.name, message.server.id, message.channel)
            except:
                self.log.info('User %s [%s], used the ' + cmd_name + ' command.',
                              message.author,
                              message.author.id)
            try:
                ch_id = str(message.channel.id)
                query = 'SELECT PREMITTED FROM NSFW WHERE CHANNEL_ID=?'
                perms = self.db.execute(query, ch_id)

                permed = 'No'

                for row in perms:
                    permed = row[0]
            except DatabaseError:
                permed = 'No'
            except SyntaxError:
                permed = 'No'
            if permed == 'Yes':
                permitted = True
            else:
                permitted = False
            # End Perms
            if permitted is True:
                # 251 x 321
                search = message.content[len(pfx) + len('nhentai') + 1:]
                try:
                    n = 0
                    list_text = '```'
                    for entry in nh.search(search)['result']:
                        n += 1
                        list_text += '\n#' + str(n) + ' ' + entry['title']['pretty']
                    if len(nh.search(search)['result']) > 1:
                        await self.client.send_message(message.channel, list_text + '\n```')
                        choice = await self.client.wait_for_message(author=message.author, channel=message.channel, timeout=20)
                        await self.client.send_typing(message.channel)
                        try:
                            nh_no = int(choice.content) - 1
                        except:
                            await self.client.send_message(message.channel,
                                                           'Not a number or timed out... Please start over')
                            return
                    else:
                        nh_no = 0
                    if nh_no > len(nh.search(search)['result']):
                        await self.client.send_message(message.channel, 'Number out of range...')
                    else:
                        hen_name = nh.search(search)['result'][nh_no]['title']['pretty']
                        hen_id = nh.search(search)['result'][nh_no]['id']
                        hen_media_id = nh.search(search)['result'][nh_no]['media_id']
                        hen_url = ('https://nhentai.net/g/' + str(hen_id) + '/')
                        hen_img = ('https://i.nhentai.net/galleries/' + str(hen_media_id) + '/1.jpg')
                        nhen_text = ''
                        nh_cover_raw = requests.get(hen_img).content
                        nh_cover_res = Image.open(BytesIO(nh_cover_raw))
                        nh_cover = nh_cover_res.resize((251, 321), Image.ANTIALIAS)
                        base = Image.open('img/ani/base.png')
                        overlay = Image.open('img/ani/overlay_nh.png')
                        base.paste(nh_cover, (100, 0))
                        base.paste(overlay, (0, 0), overlay)
                        base.save('cache\\ani\\nh_' + message.author.id + '.png')
                        for tags in nh.search(search)['result'][nh_no]['tags']:
                            nhen_text += '[' + str(tags['name']).title() + '] '
                            await self.client.send_file(message.channel, 'cache\\ani\\nh_' + message.author.id + '.png')
                            await self.client.send_message(message.channel, 'Name:\n```\n' + hen_name + '\n```\nTags:\n```\n' + nhen_text + '\n```\nBook URL: <' + hen_url + '>')
                            os.remove('cache\\ani\\nh_' + message.author.id + '.png')
                except nh.nhentai.nHentaiException as err:
                    await self.client.send_message(message.channel, str(err))
                except:
                    await self.client.send_message(message.channel, 'Nothing found or something broke...')
            else:
                await self.client.send_message(message.channel,
                                                       'This channel does not have the NSFW Module permitted!')
