import asyncio
from asyncio.tasks import sleep
from re import purge
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QDialog, QHBoxLayout, QInputDialog, QLabel, QListWidget, QMessageBox, QProgressBar, QPushButton, QVBoxLayout, QWidget
import discord
from discord.errors import LoginFailure

class App(discord.Client):
    title = "Discord Bot Spam Removal Tool"

    def __init__(self):
        super().__init__()
        self.app = QApplication([])
        self.window = QWidget()

    def run(self):
        token = self.ask_token()
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.start(token))
        except LoginFailure:
            loop.run_until_complete(self.close())
            self.show_login_fail_message()
        except KeyboardInterrupt:
            loop.run_until_complete(self.close())
    
    async def on_ready(self):
        print(self.guilds)
        ok1 = await self.ask_guild()
        if not ok1:
            await self.close()
            return

        ok2 = await self.ask_bot_channels()
        if not ok2:
            await self.close()
            return

        ok3 = await self.show_purge_dialog()
        if not ok3:
            await self.close()
            return

        await self.close()

    def ask_token(self):
        token, ok = QInputDialog.getText(None, self.title, 'Login with discord bot token:')
        if not ok:
            exit()
        return token

    async def ask_guild(self):
        guilds = self.guilds
        guildNames = list(map(lambda g: g.name, guilds))
        item, ok = QInputDialog.getItem(None, self.title, 'Select a guild to clean:', guildNames)
        if ok:
            self.guild = guilds[guildNames.index(item)]
        return ok

    async def ask_bot_channels(self):
        self.text_channels = self.guild.text_channels
        text_channel_names = list(map(lambda c: c.name, self.text_channels))

        self.channel_dialog = QDialog()
        self.channel_dialog.setWindowTitle(self.title)
        layout = QVBoxLayout(self.channel_dialog)

        dialogLabel = QLabel('Select bot channels (KEEP NOT KICK):')
        self.channelSelectWidget = QListWidget()
        self.channelSelectWidget.addItems(text_channel_names)
        self.channelSelectWidget.setSelectionMode(QListWidget.MultiSelection)

        button_layout = QHBoxLayout()
        next_button = QPushButton('Next')
        cancel_button = QPushButton('Cancel')
        next_button.clicked.connect(self.onChannelSelectNextClicked)
        cancel_button.clicked.connect(self.onCancelChannelSelectClicked)
        button_layout.addWidget(next_button)
        button_layout.addWidget(cancel_button)

        layout.addWidget(dialogLabel)
        layout.addWidget(self.channelSelectWidget)
        layout.addLayout(button_layout)

        ok = self.channel_dialog.exec() == 0
        return ok

    async def show_purge_dialog(self):
        self.purge_dialog = QDialog()
        self.purge_dialog.setWindowTitle(self.title)
        layout = QVBoxLayout(self.purge_dialog)

        self.purge_status = QLabel('Click start to purge.')
        self.pbar = QProgressBar()
        self.pbar.setMaximum(len(self.target_channels))

        self.purge_button_layout = QHBoxLayout()
        self.purge_start_btn = QPushButton('Start')
        self.purge_done_btn = QPushButton('Close')
        self.purge_done_btn.setDisabled(True)
        self.purge_start_btn.clicked.connect(self.onPurgeStart)
        self.purge_done_btn.clicked.connect(self.onPurgeDone)
        self.purge_button_layout.addWidget(self.purge_start_btn)
        self.purge_button_layout.addWidget(self.purge_done_btn)

        layout.addWidget(self.purge_status)
        layout.addWidget(self.pbar)
        layout.addLayout(self.purge_button_layout)

        ok = self.purge_dialog.exec() == 0
        return ok

    def show_login_fail_message(self):
        msg = QMessageBox(QMessageBox.Critical, self.title, "Login failed.")
        msg.exec()

    def onCancelChannelSelectClicked(self):
        self.channel_dialog.close()

    def onChannelSelectNextClicked(self):
        selected_indices = self.channelSelectWidget.selectedIndexes()
        self.target_channels = []
        for i, c in enumerate(self.text_channels):
            if not any(list(map(lambda j: j.row() == i, selected_indices))):
                self.target_channels.append(c)
        print(list(map(lambda c: c.name, self.target_channels)))
        self.channel_dialog.close()

    def onPurgeDone(self):
        self.purge_dialog.close()

    def onPurgeStart(self):
        self.purge_start_btn.setDisabled(True)
        n = len(self.target_channels)
        self.total_purged = 0
        for i, c in enumerate(self.target_channels):
            self.purge_status.setText(f'Purging {self.target_channels[i].name}... ({self.total_purged} deleted)')
            self.pbar.setValue(i)

            loop = asyncio.get_event_loop()            
            loop.run_until_complete(self.run_channel_purge(c))
        
        self.purge_status.setText(f'Purge complete! Deleted {self.total_purged} messages')
        self.pbar.setValue(n)
        self.purge_done_btn.setDisabled(False)

    async def run_channel_purge(self, channel):
        def is_me(m):
            return m.author == self.user
        deleted = await channel.purge(limit=None, check=is_me)
        self.total_purged += len(deleted)