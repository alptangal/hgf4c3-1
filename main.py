import asyncio
import json
import locale
import os
import queue
import random
import re
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta

import aiohttp
import discord
import requests
import streamlit as st
from discord import app_commands
from discord.ext import commands, tasks
from discord.utils import get
from dotenv import load_dotenv

load_dotenv()

if "log_queue" not in st.session_state:
    st.session_state["log_queue"] = queue.Queue()

if "logs" not in st.session_state:
    st.session_state["logs"] = []

if "task_running" not in st.session_state:
    st.session_state["task_running"] = False

processed_thread = set()
pause_watching = False


def myStyle(log_queue):
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    log_queue.put(("info", "Starting process data..."))

    def correctSingleQuoteJSON(s):
        rstr = ""
        escaped = False

        for c in s:
            if c == "'" and not escaped:
                c = '"'  # replace single with double quote

            elif c == "'" and escaped:
                rstr = rstr[:-1]  # remove escape character before single quotes

            elif c == '"':
                c = "\\" + c  # escape existing double quotes

            escaped = c == "\\"  # check for an escape character
            rstr += c  # append the correct json

        return rstr

    @client.event
    async def on_ready():
        global INFO, mb
        for guild in client.guilds:
            if guild.name.lower() == "llyllr's server":
                if not keepHfLive.is_running():
                    keepHfLive.start(guild)

    @tasks.loop(minutes=1)
    async def keepHfLive(guild):
        global processed_thread, mb, st, pause_watching
        print(f"keepHfLive is {'running' if not pause_watching else 'paused'}")
        log_queue.put(
            ("info", f"keepHfLive is {'running' if not pause_watching else 'paused'}")
        )
        for category in guild.categories:
            if category.name == "huggingface":
                for channel in category.channels:
                    if channel.name == "raw":
                        async for msg in channel.history():
                            if "huggingface.co" in msg.content:
                                if " || " in msg.content:
                                    space_url = msg.content.split(" || ")[0]
                                    username = space_url.split("/spaces/")[1].split(
                                        "/"
                                    )[0]
                                    space_name = space_url.split("/spaces/")[1].split(
                                        "/"
                                    )[1]
                                    authorization = msg.content.split(" || ")[1]
                                    url = f"https://{username}-{space_name}.hf.space"
                                    async with aiohttp.ClientSession() as session:
                                        async with session.get(
                                            url,
                                            headers={
                                                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Trailer/93.3.3570.29",
                                                "authorization": f"Bearer {authorization}",
                                            },
                                        ) as response:
                                            if response.status < 400:
                                                print(f"{space_url} ping success")
                                                log_queue.put(
                                                    (
                                                        "info",
                                                        f"{space_url} ping success",
                                                    )
                                                )
                                            else:
                                                print(f"{space_url} ping fail")
                                                log_queue.put(
                                                    ("error", f"{space_url} ping fail")
                                                )
                                else:
                                    space_url = msg.content.strip()
                                    username = space_url.split("/spaces/")[1].split(
                                        "/"
                                    )[0]
                                    space_name = space_url.split("/spaces/")[1].split(
                                        "/"
                                    )[1]
                                    url = f"https://{username}-{space_name}.hf.space"
                                    async with aiohttp.ClientSession() as session:
                                        async with session.get(
                                            url,
                                            headers={
                                                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Trailer/93.3.3570.29",
                                            },
                                        ) as response:
                                            if response.status < 400:
                                                print(f"{space_url} ping success")
                                                log_queue.put(
                                                    (
                                                        "info",
                                                        f"{space_url} ping success",
                                                    )
                                                )
                                            else:
                                                print(f"{space_url} ping fail")
                                                log_queue.put(
                                                    ("error", f"{space_url} ping fail")
                                                )
                            elif ".hf.space/" in msg.content:
                                if " || " in msg.content:
                                    space_url = msg.content.split(" || ")[0].strip()
                                    authorization = msg.content.split(" || ")[1].strip()
                                    async with aiohttp.ClientSession() as session:
                                        async with session.get(
                                            space_url,
                                            headers={
                                                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Trailer/93.3.3570.29",
                                                "authorization": f"Bearer {authorization}",
                                            },
                                        ) as response:
                                            if response.status < 400:
                                                print(f"{space_url} ping success")
                                                log_queue.put(
                                                    (
                                                        "info",
                                                        f"{space_url} ping success",
                                                    )
                                                )
                                            else:
                                                print(f"{space_url} ping fail")
                                                log_queue.put(
                                                    ("error", f"{space_url} ping fail")
                                                )
                                else:
                                    space_url = msg.content.strip()
                                    async with aiohttp.ClientSession() as session:
                                        async with session.get(
                                            space_url,
                                            headers={
                                                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Trailer/93.3.3570.29",
                                            },
                                        ) as response:
                                            if response.status < 400:
                                                print(f"{space_url} ping success")
                                                log_queue.put(
                                                    (
                                                        "info",
                                                        f"{space_url} ping success",
                                                    )
                                                )
                                            else:
                                                print(f"{space_url} ping fail")
                                                log_queue.put(
                                                    ("error", f"{space_url} ping fail")
                                                )

    client.run(os.environ.get("bot_token"))


thread = None


@st.cache_resource
def initialize_heavy_stuff():
    global thread
    # Đây là phần chỉ chạy ĐÚNG 1 LẦN khi server khởi động (hoặc khi cache miss)
    with st.spinner("running your scripts..."):
        thread = threading.Thread(target=myStyle, args=(st.session_state.log_queue,))
        thread.start()
        print(
            "Heavy initialization running..."
        )  # bạn sẽ thấy log này chỉ 1 lần trong console/cloud log

        return {
            "model": "loaded_successfully",
            "timestamp": time.time(),
            "db_status": "connected",
        }


# Trong phần chính của app
st.title("my style")

# Dòng này đảm bảo: chạy 1 lần duy nhất, mọi user đều dùng chung kết quả
result = initialize_heavy_stuff()

st.success("The system is ready!")
st.write("Result:")
st.json(result)
with st.status("Processing...", expanded=True) as status:
    placeholder = st.empty()
    logs = []
    while (thread and thread.is_alive()) or not st.session_state.log_queue.empty():
        try:
            level, message = st.session_state.log_queue.get_nowait()
            logs.append((level, message))

            with placeholder.container():
                for lvl, msg in logs:
                    if lvl == "info":
                        st.write(msg)
                    elif lvl == "success":
                        st.success(msg)
                    elif lvl == "error":
                        st.error(msg)

            time.sleep(0.2)
        except queue.Empty:
            time.sleep(0.3)

    status.update(label="Hoàn thành!", state="complete", expanded=False)
