import argparse
import os
import pathlib
import re
import sys
from dataclasses import dataclass
from typing import Any, Optional
from brand_cli.transcript import Transcript

from brand_cli.config import CONFIG, CONTEXT, save_context


@dataclass
class Terminology:
    ip: str = "IP"
    series: str = "Series"
    season: str = "Season"
    arc: str = "Arc"

@dataclass
class SessionData:
    season: str
    episode: str
    full_ep_id: str
    target_filename: str
    saga: str
    arc: str
    transcript_obj: 'Transcript'
    lexicon: str
    duration: float
    terms: Terminology
    uploaded_file: Optional[Any] = None


def resolve_ip_and_series(path: pathlib.Path):
    # Determine which IP and Series the transcript belongs to based on path
    content_root_cfg = CONFIG["archive"].get("content_root", "/home/bud/dev/Stream-Archive")
    content_root = pathlib.Path(content_root_cfg).resolve()
    
    ips = CONFIG.get("ips", {})
    for ip_name, ip_data in ips.items():
        series_data = ip_data.get("series", {})
        for series_name, series_info in series_data.items():
            path_relative = series_info.get("path_relative", "")
            if path_relative:
                series_root = content_root / path_relative
                if series_root in path.parents or path == series_root:
                    return ip_name, series_name, ip_data, series_info
    return None, None, None, None


def get_terminology(ip_data) -> Terminology:
    if not ip_data or "terminology" not in ip_data:
        return Terminology()
    t = ip_data["terminology"]
    return Terminology(
        ip=t.get("ip", "IP"),
        series=t.get("series", "Series"),
        season=t.get("season", "Season"),
        arc=t.get("arc", "Arc")
    )


def find_transcript_and_metadata(full_ep_id, user_ip=None, user_series=None):
    content_root_cfg = CONFIG["archive"].get("content_root", "/home/bud/dev/Stream-Archive")
    search_path = pathlib.Path(content_root_cfg).resolve()
    
    # Narrow down search if IP and Series are defined
    ip = user_ip or CONTEXT.get("ip")
    series = user_series or CONTEXT.get("series")
    
    if ip and series:
        series_cfg = CONFIG.get("ips", {}).get(ip, {}).get("series", {}).get(series, {})
        rel_path = series_cfg.get("path_relative")
        if rel_path:
            search_path = search_path / rel_path

    processed_files = list(search_path.rglob(f"{full_ep_id}/Transcript.md"))

    if processed_files:
        transcript_path = processed_files[0]
    else:
        staged_files = list(search_path.rglob(f"{full_ep_id} Transcript.md"))
        
        if not staged_files:
            return None
            
        if len(staged_files) > 1:
            print(f"Error: Multiple matches found for staging file {full_ep_id} Transcript.md.")
            for f in staged_files:
                print(f" - {f}")
            print("Please narrow your context using: python Brand.py Context --ip IP_NAME --series SERIES_NAME")
            sys.exit(1)

        old_path = staged_files[0]
        new_dir = old_path.parent / full_ep_id
        new_dir.mkdir(parents=True, exist_ok=True)
        transcript_path = new_dir / "Transcript.md"
        old_path.rename(transcript_path)
        print(f"Moved staging transcript to {transcript_path}")
    
    ip_name, series_name, ip_data, series_info = resolve_ip_and_series(transcript_path)
    
    if not series_info:
        # Fallback if unconfigured IP/Series
        series_info = {}
        ip_data = {}
        
    saga_folder_name = transcript_path.parent.parent.name
    current_dir = transcript_path.parent.parent
    arc_name = "Unknown"
    
    metadata_filename = series_info.get("arc_metadata_file", "Arc.md")

    while current_dir != search_path.parent and current_dir != current_dir.parent:
        arc_file = current_dir / metadata_filename
        if arc_file.exists():
            with open(arc_file, 'r', encoding='utf-8') as f:
                arc_name = f.read().strip()
            break
        current_dir = current_dir.parent

    if arc_name == "Unknown":
        default_arcs = series_info.get("default_arcs", {})
        arc_name = default_arcs.get(saga_folder_name, "Unknown/Multiple")

    return {
        "path": transcript_path,
        "arc": arc_name,
        "saga": saga_folder_name,
        "ip_data": ip_data,
        "series_info": series_info
    }


def _has_no_audio_transcript(file_path: str) -> bool:
    with open(file_path, 'r', encoding='utf-8') as f:
        header_chunk = f.read(500)
        if "no audio" in header_chunk.lower():
            has_no_audio = not bool(re.search(r'\d{1,2}:\d{2}', header_chunk))
            return has_no_audio
        else:
            f.seek(0)
    return False

def load_transcript_asset(file_path: str) -> str:
    if not os.path.exists(file_path):
        return ""
    if _has_no_audio_transcript(file_path):
        return ""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def read_file(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def resolve_lexicon_data(episode_str: str, series_info: dict) -> str:
    lexicon_path_cfg = series_info.get("global_lexicon_path")
    if not lexicon_path_cfg:
        return ""
        
    ep_num_match = re.search(r'(\d+)', episode_str)
    # Check if this episode is above some threshold to need a lexicon, or just load it
    if ep_num_match:
        content_root_cfg = CONFIG["archive"].get("content_root", "/home/bud/dev/Stream-Archive")
        lexicon_path = str((pathlib.Path(content_root_cfg).resolve() / lexicon_path_cfg).resolve())
        if os.path.exists(lexicon_path):
            print(f"Loading Lexicon: {lexicon_path}")
            return read_file(lexicon_path)
    return ""


def get_last_timestamp(text: str):
    ts_pattern = r'\d+:\d+:\d+\.\d+|\d+:\d+\.\d+'
    matches = re.findall(ts_pattern, text)
    return matches[-1] if matches else None


def timestamp_to_seconds(ts_str: str | None) -> float:
    if not ts_str:
        return 0.0
    try:
        parts = ts_str.split(':')
        if len(parts) == 3:
            h, m, s = parts
            total = (int(h) * 3600) + (int(m) * 60) + float(s)
        elif len(parts) == 2:
            m, s = parts
            total = (int(m) * 60) + float(s)
        else:
            total = float(parts[0])
        return round(total, 2)
    except (ValueError, IndexError):
        return 0.0


def get_video_duration(raw_content: str) -> float:
    if not raw_content:
        return 0.0
    final_ts = get_last_timestamp(raw_content)
    return timestamp_to_seconds(final_ts)


def prepare_session_assets(args) -> Optional[SessionData]:
    season = args.season or CONTEXT.get("season")
    episode = args.episode
    
    if not season and episode:
        # User only passed episode, try to find it via context season
        if CONTEXT.get("season"):
            season = CONTEXT.get("season")
        else:
            print("Error: Season must be provided either as an argument or set in Context.")
            sys.exit(1)

    full_ep_id = f"{season} {episode}"

    file_info = find_transcript_and_metadata(full_ep_id, args.ip, args.series)
    if not file_info:
        print(f"Error: Could not find '{full_ep_id} Transcript.md' or '{full_ep_id}/Transcript.md' in the configured archive paths.")
        sys.exit(1)

    transcript_data = load_transcript_asset(str(file_info['path']))
    if not transcript_data:
        print(f"Skipping {full_ep_id}: No Audio detected.")
        sys.exit(0)

    lexicon_data = resolve_lexicon_data(episode, file_info["series_info"])
    actual_duration = get_video_duration(transcript_data)
    
    terms = get_terminology(file_info["ip_data"])

    if not season:
        raise ValueError("Season must be provided")
    try:
        ts_obj = Transcript(local_path=str(file_info['path']), episode_id=full_ep_id)
        return SessionData(
            season=season,
            episode=episode,
            full_ep_id=full_ep_id,
            target_filename="Transcript.md",
            saga=str(file_info['saga']),
            arc=str(file_info['arc']),
            transcript_obj=ts_obj,
            lexicon=lexicon_data,
            duration=ts_obj.get_video_duration(),
            terms=terms
        )
    except ValueError as e:
        print(f"Skipping {full_ep_id}: {e}")
        return None


def save_audit_report(transcript_path: str, content: str, report_type: str, model_suffix: str | None = None, extension: str = ".md"):
    parent_dir = os.path.dirname(transcript_path)

    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)

    if model_suffix:
        filename = f"{report_type} - {model_suffix}{extension}"
    else:
        filename = f"{report_type}{extension}"
    save_path = os.path.join(parent_dir, filename)

    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"SUCCESS: {report_type} saved to {save_path}")


def handle_context_command(args):
    if args.clear:
        save_context({"ip": None, "series": None, "season": None})
        print("Context cleared. Operations will run in full-archive search mode.")
        sys.exit(0)
        
    current = CONTEXT.copy()
    updated = False
    
    if args.ip:
        current["ip"] = args.ip
        updated = True
    if args.series:
        current["series"] = args.series
        updated = True
    if args.season:
        current["season"] = args.season
        updated = True
        
    if updated:
        save_context(current)
        print(f"Context updated -> IP: {current['ip']} | Series: {current['series']} | Season: {current['season']}")
    else:
        print("Current Active Context:")
        print(f"  IP:     {current['ip'] or 'Not Set (Full Archive Search)'}")
        print(f"  Series: {current['series'] or 'Not Set'}")
        print(f"  Season: {current['season'] or 'Not Set'}")
        print("\nTo update, run: python Brand.py Context --ip IP_NAME --series SERIES_NAME --season SEASON_NAME")
    
    sys.exit(0)


def parse_cli_args():
    parser = argparse.ArgumentParser(description="Brand-CLI AI Orchestrator")
    parser.add_argument("operation", type=str.capitalize, choices=["Audit", "Feedback", "Gold", "Describe", "Draft", "Context"], 
                        help="The operation to execute.")
    parser.add_argument("args", nargs="*", help="[Season] Episode (e.g., S01 E005 or just E005). Not required for Context.")
    
    parser.add_argument("--ip", type=str, help="Set the IP explicitly (e.g., Valheim)")
    parser.add_argument("--series", type=str, help="Set the Series explicitly (e.g., Chronicles)")
    parser.add_argument("--season", type=str, help="Set the Season explicitly (e.g., 'Saga I')")
    parser.add_argument("--clear", action="store_true", help="Clear the active context (Context operation only)")
    parser.add_argument("--continue", dest="cont", action="store_true", help="Continue Draft to pass 2")
    
    args = parser.parse_args()
    
    if args.operation == "Context":
        handle_context_command(args)
        
    if not args.args:
        print("Error: You must provide at least the Episode (and Season, unless Context is set).")
        parser.print_help()
        sys.exit(1)
        
    if len(args.args) == 2:
        args.season = args.args[0]
        args.episode = args.args[1]
    elif len(args.args) == 1:
        # Only Episode was passed, season must come from context or --season flag
        args.episode = args.args[0]
        if not args.season and not CONTEXT.get("season"):
            print("Error: You only provided the Episode. You must provide the Season or set a default via the Context command.")
            sys.exit(1)
    else:
        print("Error: Too many positional arguments. Use '[Season] <Episode>'")
        sys.exit(1)
        
    if args.cont:
        os.environ["DRAFT_PASS"] = "2"
        
    return args
