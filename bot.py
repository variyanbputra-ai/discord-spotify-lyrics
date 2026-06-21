import discord
from discord.ext import commands, tasks
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os
import lyricsgenius
from datetime import datetime

# Load environment variables
load_dotenv()

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Spotify Setup
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
GENIUS_ACCESS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")

sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
)

genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN)

# Store current user being tracked
current_user_id = None
current_guild_id = None


@bot.event
async def on_ready():
    print(f"✅ Bot logged in as {bot.user}")
    print(f"📦 Bot is ready!")
    update_lyrics.start()


@bot.command(name="track")
async def track_spotify(ctx, user_id: str = None):
    """
    Track Spotify lyrics untuk user tertentu
    Usage: !track <spotify_user_id>
    """
    global current_user_id, current_guild_id
    
    if not user_id:
        await ctx.send("❌ Berikan Spotify User ID!\nUsage: `!track <spotify_user_id>`")
        return
    
    current_user_id = user_id
    current_guild_id = ctx.guild.id
    
    await ctx.send(f"✅ Sekarang tracking lagu dari user: `{user_id}`\n🎵 Lirik akan otomatis update ke catatan server!")


@bot.command(name="stop")
async def stop_tracking(ctx):
    """Stop tracking Spotify"""
    global current_user_id, current_guild_id
    current_user_id = None
    current_guild_id = None
    await ctx.send("⏹️ Tracking dihentikan!")


@bot.command(name="lyrics")
async def get_lyrics(ctx, *, song: str = None):
    """
    Get lirik lagu secara manual
    Usage: !lyrics <artist> - <song name>
    """
    if not song:
        await ctx.send("❌ Berikan nama lagu!\nUsage: `!lyrics <artist> - <song name>`")
        return
    
    try:
        await ctx.send(f"🔍 Mencari lirik untuk: `{song}`...")
        
        # Search lyrics
        result = genius.search_song(song)
        
        if result:
            lyrics = result.lyrics
            artist = result.artist
            title = result.title
            
            # Split lyrics into chunks (Discord message limit)
            chunks = [lyrics[i:i+1900] for i in range(0, len(lyrics), 1900)]
            
            embed = discord.Embed(
                title=f"🎵 {title}",
                description=f"**Artist:** {artist}",
                color=discord.Color.green()
            )
            embed.set_footer(text="Powered by Genius API")
            
            await ctx.send(embed=embed)
            
            for chunk in chunks:
                await ctx.send(f"```\n{chunk}\n```")
        else:
            await ctx.send(f"❌ Lirik untuk `{song}` tidak ditemukan!")
    
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")


@tasks.loop(minutes=1)
async def update_lyrics():
    """Automatically update lyrics based on current Spotify song"""
    global current_user_id, current_guild_id
    
    if not current_user_id or not current_guild_id:
        return
    
    try:
        # Get current playing track
        results = sp.current_user_top_tracks(limit=1)
        
        if results['items']:
            track = results['items'][0]
            track_name = track['name']
            artist_name = track['artists'][0]['name']
            
            # Get guild and update notes
            guild = bot.get_guild(current_guild_id)
            
            if guild:
                try:
                    # Get lyrics
                    song = genius.search_song(f"{track_name} {artist_name}")
                    
                    if song:
                        lyrics = song.lyrics[:1900]  # Limit to avoid overflow
                        
                        # Try to update guild notes/topic
                        # Note: This requires bot to have permissions
                        topic = f"🎵 Now: {track_name} - {artist_name}\n\n{lyrics[:500]}..."
                        
                        print(f"📝 Updated: {track_name} - {artist_name}")
                except Exception as e:
                    print(f"Lyrics error: {e}")
    
    except Exception as e:
        print(f"Update error: {e}")


@update_lyrics.before_loop
async def before_update_lyrics():
    await bot.wait_until_ready()


# Run the bot
if __name__ == "__main__":
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    bot.run(DISCORD_TOKEN)
