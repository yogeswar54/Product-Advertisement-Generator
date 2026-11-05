from app.video.assembly import get_job, start_video_job


def test_missing_ffmpeg_job(monkeypatch, tmp_path):
    import app.video.assembly as assembly
    monkeypatch.setattr(assembly.shutil, "which", lambda name: None)
    job = start_video_job("campusflow", 15, b"placeholder wav")
    import time
    time.sleep(0.05)
    status = get_job(job["job_id"])
    assert status["status"] == "failed"
    assert "FFmpeg" in status["error"]


def test_mock_ffmpeg_success(monkeypatch, tmp_path):
    import app.video.assembly as assembly
    import app.services.asset_storage as storage
    monkeypatch.setattr(assembly.shutil, "which", lambda name: "ffmpeg")
    monkeypatch.setattr(storage, "ASSET_ROOT", tmp_path)
    monkeypatch.setattr(storage, "METADATA_PATH", tmp_path / "metadata.json")
    monkeypatch.setattr(assembly, "ASSET_ROOT", tmp_path)
    def fake_run(command, check, capture_output):
        tmp = __import__('pathlib').Path(command[-1])
        tmp.write_bytes(b"placeholder mp4")
        return None
    monkeypatch.setattr(assembly.subprocess, "run", fake_run)
    job = start_video_job("campusflow", 15, b"placeholder wav")
    import time
    time.sleep(0.1)
    status = get_job(job["job_id"])
    assert status["status"] == "completed"
    assert status["asset_id"]


def test_assembly_job_start():
    job = start_video_job("campusflow", 15, b"placeholder wav")
    assert job["job_id"]
    assert job["status"] in {"queued", "running", "failed"}
