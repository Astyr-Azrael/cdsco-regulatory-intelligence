"""Build a local submission archive with an integrity manifest and frozen evidence."""
from __future__ import annotations
import hashlib
import json
import sqlite3
import subprocess
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile,ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[1]


def main():
    paths=set()
    for folder in ("backend/app","backend/tests","scripts","frontend/src","docs","data/samples","data/interim","dist"):
        for path in (ROOT/folder).rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts and path.suffix not in {".pyc",".pdf"} and path.name!="Smart_EV_Journey_Planner_Team_Contribution_Report.docx":
                paths.add(path)
    for name in ("README.md","requirements.txt","Dockerfile","docker-compose.yml","alembic.ini","pytest.ini",".env.example",".gitignore","PROJECT_KNOWLEDGE.md","PHASE2_ROW_EXTRACTION_AND_FRONTEND_REFINEMENT.md",
                 "frontend/package.json","frontend/package-lock.json","frontend/index.html","frontend/vite.config.js","frontend/Dockerfile","frontend/nginx.conf","frontend/.nvmrc"):
        path=ROOT/name
        if path.exists(): paths.add(path)
    verification=json.loads((ROOT/"docs/release-verification.json").read_text(encoding="utf-8"))
    for source in verification["corpus"]:
        paths.add(ROOT/source["local_raw_path"].replace("\\","/"))
    paths.update((ROOT/"data/raw/html").glob("*.html"))
    output=ROOT/"releases/CDSCO_Final_Local_Demo_2026-10-19.zip"
    output.parent.mkdir(exist_ok=True)
    manifest={"release":"2026-10-19","git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
              "scope":"Frozen local academic demo; no virtual environments, dependencies, secrets or unrelated documents.",
              "files":{}}
    scratch=ROOT/".pytest-runs"
    scratch.mkdir(exist_ok=True)
    with TemporaryDirectory(dir=scratch) as temporary:
        backup=Path(temporary)/"cdsco_demo.db"
        with closing(sqlite3.connect(ROOT/"data/cdsco_demo.db")) as source,closing(sqlite3.connect(backup)) as target:
            source.backup(target)
        with ZipFile(output,"w",ZIP_DEFLATED) as bundle:
            for path in sorted(paths):
                name=path.relative_to(ROOT).as_posix()
                content=path.read_bytes()
                manifest["files"][name]=hashlib.sha256(content).hexdigest()
                bundle.writestr(name,content)
            content=backup.read_bytes()
            manifest["files"]["data/cdsco_demo.db"]=hashlib.sha256(content).hexdigest()
            bundle.writestr("data/cdsco_demo.db",content)
            bundle.writestr("SUBMISSION_MANIFEST.json",json.dumps(manifest,indent=2))
    with ZipFile(output) as bundle:
        assert bundle.testzip() is None
        for name,digest in manifest["files"].items():
            assert hashlib.sha256(bundle.read(name)).hexdigest()==digest
    print(json.dumps({"archive":str(output),"files":len(manifest["files"]),"bytes":output.stat().st_size,"sha256":hashlib.sha256(output.read_bytes()).hexdigest()},indent=2))


if __name__=="__main__":main()
