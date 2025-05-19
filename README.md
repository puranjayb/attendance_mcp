
# MCP server for attendance-management

So yeah I tried MCP server handson and this is what I made. A tool for you to manage attendance-system in your class, you can.
1. Create/Update/Delete a class.
2. Create/Update/Delete a student.
3. Check Attendance of whole class / Individual.
4. Get details of all classes / Particular.
5. Get details of students/student.

## MCP server setup

### Requirements
1. Claude Desktop (I used this) / Any other MCP supported application.
2. Python Enviornment >=3.13.3
3. Node Enviornment (Maybe) >= 22.0.5 (lts)
4. MongoDB server

### Preferred Method
1. Create a UV project [Follow the instructions here.](https://docs.astral.sh/uv/getting-started/installation/)
2. Clone this repository.
```pwsh
git clone https:www.github.com/puranjayb/attendance_mcp.git
cd attendance_mcp
```
3. Sync the dependencies from pyproject.toml
```pwsh
uv sync
uv lock
```
6. Create a .env file
```env
MONGO_URI=<youruri>
DB_NAME=<dbname>
```
5. Install the MCP server
```pwsh
uv run mcp install main.py -f .env
```
5. Go to C:\Users\username\AppData\Roaming\Claude and edit claude_desktop_config.json
```json
{
  "mcpServers": {
    "attendance_mcp": {
      "command": "C:\\Users\\<username>\\.local\\bin\\uv.EXE",
      "args": [
        "run",
        "--with",
        "mcp[cli],pymongo", // Add pymongo here
        "mcp",
        "run",
        "main.py file directory"
      ],
      "env": {
        "MONGO_URI": "your uri",
        "DB_NAME": "your db name"
      }
    }
  }
}
```
6. You can open and use this MCP on your claude desktop enviornment

