import logging
import random
import re
from openai import AsyncOpenAI, APIError
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self, model: str = "gpt-3.5-turbo-0125"):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = model

    async def generate_comment(
            self,
            tone: str,
            post_text: str,
            max_retries: int = 2
    ) -> Optional[str]:
        """Генерация контекстных комментариев с учетом тона"""
        for attempt in range(max_retries):
            try:
                prompt = self._build_prompt(tone, post_text)
                logger.debug(f"Generated prompt: {prompt}")

                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=300
                )
                comment = response.choices[0].message.content
                validated_comment = self._validate_comment(comment, post_text)
                logger.debug(f"Validated comment: {validated_comment}")
                return validated_comment
            except Exception as e:
                logger.error(f"Ошибка генерации (попытка {attempt + 1}): {str(e)}")
                await asyncio.sleep(1)
        return self._smart_fallback(post_text, tone)

    @staticmethod
    def _build_prompt(tone: str, post_text: str) -> str:
        """Построение продвинутого промпта"""
        tone_instructions = {
            "positive": "Сделай акцент на положительных аспектах из поста. Пример: 'Отличная идея насчет...'",
            "neutral": "Вырази нейтральное мнение с анализом. Пример: 'Интересно, как это работает при...'",
            "critical": "Укажи на спорные моменты конструктивно. Пример: 'Возможно стоит учесть...'",
            "question": "Задай вопрос по ключевой идее. Пример: 'Как именно работает...?'"
        }
        return (
            f"Напиши {tone} комментарий для поста в Telegram. {tone_instructions.get(tone, '')}\n"
            f"Текст поста:\n---\n{post_text}\n---\n"
            "Требования:\n"
            "1. Упоминай конкретные элементы из поста\n"
            "2. Естественный разговорный стиль\n"
            "3. 1-2 предложения\n"
            "4. Без эмодзи/хештегов"
        )

    def _validate_comment(self, comment: str, post_text: str) -> str:
        """Проверка релевантности комментария"""
        comment = comment.strip()
        if len(comment) < 20:
            raise ValueError("Слишком короткий комментарий")

        post_keywords = self._extract_keywords(post_text)
        comment_keywords = self._extract_keywords(comment)

        if not set(post_keywords).intersection(comment_keywords):
            raise ValueError("Комментарий не связан с постом")

        return comment[:500]

    @staticmethod
    def _extract_keywords(text: str) -> list:
        """Извлечение ключевых слов с фильтрацией"""
        words = re.findall(r'\b\w{5,}\b', text.lower())
        return list(set(words))[:5]

    def _smart_fallback(self, post_text: str, tone: str) -> str:
        """Умные фол бек-комментарии"""
        keywords = self._extract_keywords(post_text)
        templates = {
            "positive": [
                f"Отличная статья про {keywords[0]}!",
                f"{keywords[0]} - это действительно важно"
            ],
            "neutral": [
                f"Как связано {keywords[0]} и {keywords[1]}?",
                f"Для понимания {keywords[0]} нужно учесть..."
            ],
            "critical": [
                f"Сомнения насчет {keywords[0]}",
                f"Не учтено {keywords[1]} в этом подходе"
            ],
            "question": [
                f"Как работает {keywords[0]}?",
                f"Почему важно {keywords[1]}?"
            ]
        }
        return random.choice(templates.get(tone, ["Интересный пост!"]))