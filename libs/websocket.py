import asyncio
import websockets
import json

class WebSocketReader:
    """
    WebSocketReader is a class that handles WebSocket connections to Binance and broadcasts messages to connected clients.

    Attributes:
        coins (list): A list of coin symbols to subscribe to on Binance.
        binance_ws_url (str): The WebSocket URL for Binance. Defaults to "wss://fstream.binance.com/ws".
        clients (set): A set of connected WebSocket clients.

    Methods:
        __init__(self, coins, binance_ws_url="wss://fstream.binance.com/ws"):
            Initializes the WebSocketReader with a list of coins and an optional Binance WebSocket URL.

        async binance_handler(self, websocket):
            Handles incoming messages from Binance and broadcasts them to connected clients.

        async broadcast(self, message):
            Broadcasts a message to all connected clients.

        async connect_to_binance(self):
            Connects to the Binance WebSocket and starts handling messages.

        async start_server(self, host="localhost", port=8765):
            Starts a WebSocket server that listens for incoming client connections.

            Runs the WebSocket server and connects to Binance, handling both concurrently.
    """
    def __init__(self, coins, binance_ws_url="wss://fstream.binance.com/ws"):
        self.coins = coins
        self.binance_ws_url = binance_ws_url
        self.clients = set()

    async def binance_handler(self, websocket):
        """
        Handles incoming WebSocket connections from Binance.

        This coroutine adds the WebSocket connection to the set of clients,
        listens for incoming messages, processes them, and broadcasts the
        data to all connected clients. When the connection is closed, it
        removes the WebSocket from the set of clients.

        Args:
            websocket (WebSocket): The WebSocket connection to handle.

        Raises:
            json.JSONDecodeError: If the incoming message is not valid JSON.
        """
        self.clients.add(websocket)
        try:
            async for message in websocket:
                data = json.loads(message)
                await self.broadcast(data)
        finally:
            self.clients.remove(websocket)

    async def broadcast(self, message):
        """
        Broadcasts a message to all connected clients.

        Args:
            message (dict): The message to be sent to all clients. It will be converted to a JSON string.

        Returns:
            None

        Raises:
            asyncio.TimeoutError: If sending the message to any client takes too long.
        """
        if self.clients:
            await asyncio.wait([client.send(json.dumps(message)) for client in self.clients])

    async def connect_to_binance(self):
        """
        Connects to the Binance WebSocket API and listens for ticker updates for the specified coins.

        This method constructs the WebSocket URL using the provided list of coins and connects to the Binance WebSocket API.
        It then awaits and handles incoming messages using the `binance_handler` method.

        Args:
            None

        Returns:
            None

        Raises:
            websockets.exceptions.WebSocketException: If there is an issue with the WebSocket connection.
        """
        streams = "/".join([f"{coin.lower()}@ticker" for coin in self.coins])
        url = f"{self.binance_ws_url}/{streams}"
        async with websockets.connect(url) as websocket:
            await self.binance_handler(websocket)

    async def start_server(self, host="localhost", port=8765):
        """
        Starts a WebSocket server.

        This asynchronous method initializes and starts a WebSocket server that listens on the specified host and port.
        The server will handle incoming WebSocket connections using the `binance_handler` method.

        Args:
            host (str): The hostname to listen on. Defaults to "localhost".
            port (int): The port number to listen on. Defaults to 8765.

        Returns:
            None
        """
        server = await websockets.serve(lambda ws, _: self.binance_handler(ws), host, port)
        await server.wait_closed()

    def run(self):
        """
        Runs the asyncio event loop until all specified coroutines are complete.

        This method initializes the asyncio event loop and runs it until the 
        coroutines `self.start_server()` and `self.connect_to_binance()` are 
        completed.

        Raises:
            Exception: If the event loop fails to run the coroutines.
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(
            self.start_server(),
            self.connect_to_binance()
        ))