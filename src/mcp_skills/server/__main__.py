from mcp_skills.server.app import build_server
from mcp_skills.config import settings

def main():
    mcp = build_server(settings)
    mcp.run()

if __name__ == "__main__":
    main()
