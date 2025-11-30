"""抽象的な LLM クライアント インターフェース."""

from abc import ABC, abstractmethod


class ChatClient(ABC):
    """LLM プロバイダーの抽象インターフェース.

    すべての具体的なクライアント実装はこのインターフェースを継承する。
    """

    @abstractmethod
    def send_message(
        self,
        system: str,
        user: str,
        temperature: float = 0.7,
    ) -> str:
        """メッセージを送信して レスポンスを取得する.

        Args:
            system: システムプロンプト
            user: ユーザーメッセージ
            temperature: サンプリング温度 (0.0-2.0)

        Returns:
            LLM からのレスポンステキスト

        Raises:
            LLMCallError: リクエスト失敗時
        """
        pass

    @abstractmethod
    async def send_message_async(
        self,
        system: str,
        user: str,
        temperature: float = 0.7,
    ) -> str:
        """非同期版: メッセージを送信してレスポンスを取得する.

        Args:
            system: システムプロンプト
            user: ユーザーメッセージ
            temperature: サンプリング温度 (0.0-2.0)

        Returns:
            LLM からのレスポンステキスト

        Raises:
            LLMCallError: リクエスト失敗時
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """プロバイダー名を返す.

        Returns:
            プロバイダー名 ('openai', 'anthropic' など)
        """
        pass
