"""Check kit hashes and build/run isolated consumers for wire v1 or v2."""
import argparse
import hashlib
import json
import os
from pathlib import Path

def require(ok, message):
    if not ok: raise RuntimeError(message)
import subprocess
import tempfile
import zipfile

R = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--cmake', default='cmake')
p.add_argument('--wire-major', type=int, choices=[1, 2], default=1)
a = p.parse_args()

def sha(b):
    return hashlib.sha256(b).hexdigest()

major = a.wire_major
dist = R / 'dist' if major == 1 else R / 'dist/v2'
manifest = json.loads((dist / 'handoff-manifest.json').read_text())
archive = dist / manifest['artifact']
require(manifest['wire_version'] == {'major': major, 'minor': 0}, "Validation failed: manifest['wire_version'] == {'major': major, 'minor': 0}")
require(sha(archive.read_bytes()) == manifest['sha256'], "Validation failed: sha(archive.read_bytes()) == manifest['sha256']")

namespace = f'v{major}'
fixture_root = 'fixtures/valid' if major == 1 else 'fixtures/v2'
message_names = ['observation', 'device-state', 'mtp-pose', 'tracker-state']

with tempfile.TemporaryDirectory(prefix=f'monaka-kit-v{major}-') as directory:
    w = Path(directory)
    kit = w / 'third_party/monaka-protocol'
    require(w.resolve().parent == Path(tempfile.gettempdir()).resolve(), 'Validation failed: w.resolve().parent == Path(tempfile.gettempdir()).resolve()')
    with zipfile.ZipFile(archive) as z:
        require(all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist()), "Validation failed: all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist())")
        z.extractall(kit)

    lock = json.loads((kit / 'protocol.lock.json').read_text())
    require(lock['wire_version'] == {'major': major, 'minor': 0}, "Validation failed: lock['wire_version'] == {'major': major, 'minor': 0}")
    require(sha((kit / 'protocol.lock.json').read_bytes()) == manifest['protocol_lock_sha256'], "Validation failed: sha((kit / 'protocol.lock.json').read_bytes()) == manifest['protocol_lock_sha256']")
    require(lock['source_commit'] == manifest['source_commit'] and lock['schema_commit'] == manifest['schema_commit'], "Validation failed: lock['source_commit'] == manifest['source_commit'] and lock['schema_commit'] == manifest['schema_commit']")
    for line in (kit / 'SHA256SUMS').read_text().splitlines():
        h, n = line.split('  ', 1)
        require(sha((kit / n).read_bytes()) == h, n)
    for n, h in lock['files_sha256'].items():
        require(sha((kit / n).read_bytes()) == h, n)
    for n, info in lock['toolchain_and_dependencies']['vendored_files'].items():
        require(sha((kit / n).read_bytes()) == info['sha256'], n)

    (w / 'CMakeLists.txt').write_text('''cmake_minimum_required(VERSION 3.20)
project(KitConsumer LANGUAGES CXX)
add_subdirectory(third_party/monaka-protocol/cpp)
add_executable(consumer main.cpp)
target_link_libraries(consumer PRIVATE MonakaProtocol::Codec)
''')
    (w / 'main.cpp').write_text(f'''#include <monaka/protocol/{namespace}/codec.hpp>
#include <fstream>
#include <iterator>
#include <string>
int main(int argc,char** argv) {{
  if(argc!=2) return 1;
  std::ifstream f(argv[1],std::ios::binary);
  std::string b((std::istreambuf_iterator<char>(f)),{{}}), encoded;
  monaka::protocol::{namespace}::Envelope out; monaka::protocol::{namespace}::Error error;
  if(!monaka::protocol::{namespace}::DecodeEnvelope(reinterpret_cast<const uint8_t*>(b.data()),b.size(),out,error)) return 2;
  return monaka::protocol::{namespace}::EncodeEnvelope(out,encoded,error)?0:3;
}}
''')

    def run(cmd):
        subprocess.run([str(x) for x in cmd], cwd=w, check=True)

    run([a.cmake, '-S', '.', '-B', 'build', '-DCMAKE_BUILD_TYPE=Release'])
    run([a.cmake, '--build', 'build', '--config', 'Release'])
    binary = w / ('build/Release/consumer.exe' if os.name == 'nt' else 'build/consumer')
    for name in message_names:
        run([binary, kit / f'{fixture_root}/{name}.json'])

    (w / 'Consumer.java').write_text(f'''import dev.monaka.protocol.{namespace}.*;
import java.nio.file.*;
public class Consumer {{
 public static void main(String[] args) throws Exception {{
  DecodeResult r = MonakaCodec.decodeEnvelope(Files.readAllBytes(Path.of(args[0])));
  if (!(r instanceof DecodeResult.Success)) throw new AssertionError(r);
  if (!(MonakaCodec.encodeEnvelope(((DecodeResult.Success)r).getValue()) instanceof EncodeResult.Success)) throw new AssertionError();
 }}
}}
''')
    cp = str(kit / 'jvm/libs/*')
    run(['javac', '--release', '17', '-cp', cp, 'Consumer.java'])
    for name in message_names:
        run(['java', '-cp', '.' + os.pathsep + cp, 'Consumer', kit / f'{fixture_root}/{name}.json'])

print(f'PASS v{major} external ZIP hash, internal file/lock/dependency hashes and isolated C++/JVM consumers (4 messages each)')
(R / f'build/kit-verification-v{major}.json').write_text(json.dumps({
    'status': 'PASS',
    'wire_version': {'major': major, 'minor': 0},
    'sha256': manifest['sha256'],
    'source_commit': manifest['source_commit'],
    'cpp_messages': 4,
    'jvm_messages': 4,
}, indent=2) + '\n')
