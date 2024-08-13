from telethon import TelegramClient, events
from telethon.tl.types import PeerUser
import os
import datetime
import random

# Remplace par tes propres informations
api_id = ''
api_hash = ''
phone_number = ''

# Initialisation du client
client = TelegramClient('session_name', api_id, api_hash)

user_message_ids = {}
user_message_ids_previous = {}

emojis = ["✉️", "📁", "📝", "🚀", "🔍", "🗑️", "📜", "❓"]

def get_random_emoji():
    return random.choice(emojis)

async def save_message(username, message_text, user_id):
    user_folder = f"{user_id}" if username is None else username
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    
    text_file_path = os.path.join(user_folder, f"{user_id}.txt")
    if not os.path.exists(text_file_path):
        with open(text_file_path, 'w', encoding='utf-8') as file:
            pass
    
    with open(text_file_path, 'a', encoding='utf-8') as file:
        file.write(f"{message_text}\n")
    
    print(f"{get_random_emoji()} Message enregistré pour {username or user_id}: {message_text} 🕵️")

async def save_media(user_id, media_data, media_type, media_name):
    user_folder = f"{user_id}"
    media_folder = os.path.join(user_folder, 'media')
    
    if not os.path.exists(media_folder):
        os.makedirs(media_folder)
    
    media_file_path = os.path.join(media_folder, media_name)
    
    with open(media_file_path, 'wb') as file:
        file.write(media_data)
    
    media_list_file_path = os.path.join(user_folder, 'media_list.txt')
    with open(media_list_file_path, 'a', encoding='utf-8') as file:
        file.write(f"{media_name} ({media_type})\n")
    
    print(f"{get_random_emoji()} {media_type} enregistré pour {user_id}: {media_file_path} 🕵️")

async def log_cleared_conversation(user_id):
    user_folder = f"{user_id}"
    clear_file_path = os.path.join(user_folder, 'clear_conversation.txt')
    
    with open(clear_file_path, 'a', encoding='utf-8') as file:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"❗ Conversation effacée à {now}\n")
    
    print(f"{get_random_emoji()} Conversation effacée pour {user_id} : Enregistré dans {clear_file_path} 🕵️")

async def fetch_old_messages():
    async for dialog in client.iter_dialogs():
        if isinstance(dialog.entity, PeerUser):
            user = dialog.entity
            user_id = user.id
            username = user.username if user.username else None
            print(f"{get_random_emoji()} Récupération des messages pour {username or user_id}...")

            user_message_ids[user_id] = set()
            
            async for message in client.iter_messages(user_id, limit=1000):
                if message.id not in user_message_ids[user_id]:
                    user_message_ids[user_id].add(message.id)
                    if message.text:
                        await save_message(username, message.text, user_id)
                    if message.photo:
                        file_path = await message.download_media()
                        media_data = open(file_path, 'rb').read()
                        media_name = f"{user_id}_{message.id}.jpg"
                        await save_media(user_id, media_data, 'Image', media_name)
                        os.remove(file_path)
                    elif message.video:
                        file_path = await message.download_media()
                        media_data = open(file_path, 'rb').read()
                        media_name = f"{user_id}_{message.id}.mp4"
                        await save_media(user_id, media_data, 'Vidéo', media_name)
                        os.remove(file_path)
                    elif message.document:
                        file_path = await message.download_media()
                        media_data = open(file_path, 'rb').read()
                        media_name = f"{user_id}_{message.id}.pdf"
                        await save_media(user_id, media_data, 'Document', media_name)
                        os.remove(file_path)

            print(f"{get_random_emoji()} Messages anciens récupérés pour {username or user_id} 🕵️")

@client.on(events.NewMessage)
async def handler(event):
    if isinstance(event.chat_id, int):
        sender = await event.get_sender()
        if sender:
            user_id = sender.id
            username = sender.username if sender.username else None
            message_text = event.message.text
            
            if message_text:
                await save_message(username, message_text, user_id)
            else:
                if event.message.photo:
                    file_path = await event.message.download_media()
                    media_data = open(file_path, 'rb').read()
                    media_name = f"{user_id}_{event.message.id}.jpg"
                    await save_media(user_id, media_data, 'Image', media_name)
                    os.remove(file_path)
                elif event.message.video:
                    file_path = await event.message.download_media()
                    media_data = open(file_path, 'rb').read()
                    media_name = f"{user_id}_{event.message.id}.mp4"
                    await save_media(user_id, media_data, 'Vidéo', media_name)
                    os.remove(file_path)
                elif event.message.document:
                    file_path = await event.message.download_media()
                    media_data = open(file_path, 'rb').read()
                    media_name = f"{user_id}_{event.message.id}.pdf"
                    await save_media(user_id, media_data, 'Document', media_name)
                    os.remove(file_path)
                else:
                    print(f"🚫 Message reçu mais sans texte ni média : {event.message.text}")
            
            if user_id in user_message_ids:
                user_message_ids[user_id].add(event.message.id)
        else:
            print(f"❓ Message reçu d'un expéditeur inconnu : {event.message.text}")
    else:
        print("🚫 Message reçu d'une source non identifiée.")

@client.on(events.MessageDeleted)
async def handle_message_deleted(event):
    if event.chat_id in user_message_ids:
        deleted_message_ids = event.deleted_ids
        if deleted_message_ids:
            remaining_message_ids = user_message_ids[event.chat_id] - set(deleted_message_ids)
            if not remaining_message_ids:
                await log_cleared_conversation(event.chat_id)
                print(f"{get_random_emoji()} Tous les messages pour {event.chat_id} ont été supprimés.")
            user_message_ids[event.chat_id] = remaining_message_ids
        else:
            if event.chat_id in user_message_ids_previous and not user_message_ids[event.chat_id]:
                await log_cleared_conversation(event.chat_id)
                print(f"{get_random_emoji()} Tous les messages pour {event.chat_id} ont été supprimés (initial).")
    else:
        user_message_ids_previous[event.chat_id] = user_message_ids.get(event.chat_id, set())

async def main():
    await client.start(phone_number)
    print(f"{get_random_emoji()} Client en cours d'exécution...")

    await fetch_old_messages()
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    print(f"{get_random_emoji()} 🔐 Initialisation du script... Veuillez patienter.")
    with client:
        client.loop.run_until_complete(main())
