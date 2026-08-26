import uuid
import time
from datetime import datetime, timezone

random_string = str(uuid.uuid4())
file_path = "/shared/output.log"

while True:
    timestamp = datetime.now(timezone.utc).isoformat()
    line = f"{timestamp}: {random_string}"

    with open(file_path, "w") as f:
        f.write(line)

    print(line, flush=True)

    time.sleep(5)