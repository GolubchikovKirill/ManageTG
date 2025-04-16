import asyncio
import os
import random
from pyrogram import Client, errors
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Actions, Channels
from services.openai_service import OpenAIService


class BotActionExecutor:
    def __init__(self, session: AsyncSession, openai_service: OpenAIService, session_folder: str = "sessions"):
        self.session = session
        self.openai_service = openai_service
        self.session_folder = session_folder

    @staticmethod
    def random_time_with_spread(time_frame: int, spread_percent: int) -> int:
        spread = time_frame * spread_percent / 100
        return random.randint(
            int((time_frame - spread) * 60),
            int((time_frame + spread) * 60)
        )

    async def get_channel(self, channel_id: int) -> Channels | None:
        result = await self.session.execute(
            select(Channels).where(Channels.id == channel_id)
        )
        return result.scalars().first()

    async def execute_action(self, action: Actions, bot_client: Client):
        try:
            delay_minutes = self.random_time_with_spread(action.action_time, action.random_percentage)
            print(f"Waiting for {delay_minutes} minutes before performing action.")
            await asyncio.sleep(delay_minutes * 60)

            if action.action_type == "comment":
                await self.execute_comment(action.channel_id, action.count, bot_client)
            elif action.action_type == "reaction":
                await self.execute_reaction(action.channel_id, action.count, bot_client)
            elif action.action_type == "view":
                await self.execute_view(action.channel_id, action.count, bot_client)
        except errors.FloodWait as e:
            print(f"FloodWait error: {e}")
            await asyncio.sleep(e.value * 60)
        except Exception as e:
            print(f"Error executing action: {e}")

    async def execute_comment(self, channel_id: int, count: int, bot_client: Client):
        channel = await self.get_channel(channel_id)
        if not channel:
            print(f"Channel {channel_id} not found.")
            return

        try:
            chat = await bot_client.get_chat(channel.name)
            print(f"📢 Channel: {chat.title} (ID: {chat.id})")

            if not chat.linked_chat:
                print("❌ Channel has no linked discussion group")
                return

            discussion_group = await bot_client.get_chat(chat.linked_chat.id)
            print(f"💬 Discussion group: {discussion_group.title} (ID: {discussion_group.id})")

            # Join group if not member
            try:
                await bot_client.get_chat_member(discussion_group.id, "me")
            except errors.UserNotParticipant:
                print("🤖 Joining discussion group...")
                try:
                    await bot_client.join_chat(discussion_group.username or discussion_group.id)
                    print("✅ Joined successfully")
                    await asyncio.sleep(5)
                except Exception as e:
                    print(f"❌ Join error: {e}")
                    return

            # Check permissions
            try:
                member = await bot_client.get_chat_member(discussion_group.id, "me")
                print(f"🔑 Member status: {member.status}")

                if member.status == "administrator":
                    if not member.privileges or not member.privileges.can_post_messages:
                        print("❌ Admin lacks posting privileges")
                        return
                    print("👑 Admin with posting rights confirmed")
                else:
                    if not discussion_group.permissions or not discussion_group.permissions.can_send_messages:
                        print("❌ Group permissions restrict messaging")
                        return
                    print("👤 Regular member with messaging rights confirmed")

            except Exception as e:
                print(f"❌ Permission check failed: {e}")
                return

            # Get 3 last posts
            last_posts = []
            async for message in bot_client.get_chat_history(chat.id, limit=10):
                if not message.service and (message.text or message.caption):
                    last_posts.append(message)
                    if len(last_posts) >= 3:  # Собираем 3 последних поста
                        break

            if not last_posts:
                print("➖ No suitable posts found")
                return

            print(f"📌 Found {len(last_posts)} recent posts:")
            for i, post in enumerate(last_posts, 1):
                print(f"#{i} ID: {post.id} | Date: {post.date} | Link: https://t.me/c/{chat.id}/{post.id}")

            # Calculate comments per post
            comments_per_post = max(1, count // len(last_posts))
            print(f"\n📝 Will send {comments_per_post} comments per post")

            # Process each post
            total_sent = 0
            for post in last_posts:
                try:
                    print(f"\n🎯 Processing post ID {post.id}")

                    for comment_num in range(comments_per_post):
                        comment_text = await self.openai_service.generate_comment()
                        if not comment_text:
                            print("⚠️ Failed to generate comment")
                            continue

                        await bot_client.send_message(
                            chat_id=discussion_group.id,
                            text=comment_text,
                            reply_to_message_id=post.id
                        )
                        total_sent += 1
                        print(f"✅ Comment #{comment_num + 1} sent")

                        delay = random.randint(15, 30)
                        print(f"⏳ Next action in {delay}s")
                        await asyncio.sleep(delay)

                except errors.ReplyMessageMissing:
                    print("⚠️ Post has been deleted, skipping")
                except Exception as e:
                    print(f"⚠️ Error: {type(e).__name__} - {e}")
                    await asyncio.sleep(10)

            print(f"\n📊 Total comments sent: {total_sent}/{count}")

        except errors.ChatAdminRequired as e:
            print(f"🚫 Admin required: {e}")
        except Exception as e:
            print(f"🔥 Critical error: {type(e).__name__} - {e}")

    async def execute_view(self, channel_id: int, count: int, bot_client: Client):
        channel = await self.get_channel(channel_id)
        if not channel:
            print(f"Channel {channel_id} not found.")
            return

        try:
            counter = 0
            async for message in bot_client.get_chat_history(
                    channel.name,
                    limit=min(count, 100)
            ):
                if message.photo or message.video:
                    try:
                        await bot_client.download_media(message, file_name=os.devnull)
                        counter += 1
                    except Exception as e:
                        print(f"⚠️ Media error: {e}")
                await asyncio.sleep(random.uniform(0.5, 2.5))
                if counter >= count:
                    break
            print(f"👀 Processed {counter} views")
        except Exception as e:
            print(f"View error: {e}")

    def load_sessions(self):
        if not os.path.exists(self.session_folder):
            os.makedirs(self.session_folder, exist_ok=True)
            return []

        return [
            f.split(".")[0]
            for f in os.listdir(self.session_folder)
            if f.endswith(".session")
        ]

    async def run(self, action: Actions, api_id: str, api_hash: str):
        sessions = self.load_sessions()
        tasks = []

        for session_name in sessions:
            session_path = os.path.join(self.session_folder, f"{session_name}.session")

            async def task_wrapper(path=session_path):
                try:
                    async with Client(
                            name=session_name,
                            api_id=api_id,
                            api_hash=api_hash,
                            workdir=self.session_folder
                    ) as client:
                        await self.execute_action(action, client)
                except Exception as e:
                    print(f"Session {path} error: {e}")

            tasks.append(asyncio.create_task(task_wrapper()))

        await asyncio.gather(*tasks, return_exceptions=True)
        return {"status": "completed", "sessions_processed": len(sessions)}