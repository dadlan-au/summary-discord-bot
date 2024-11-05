# Product Requirements Document (PRD)

## Project Overview

The project is a Python Discord bot that connects to a single guild server and provides a range of commands.
The bot supports a range of commands, for example:

- **`tix`**: Calls a module and method that returns an embedded image message.
- **`digest`**: Calls another module and method that returns an embedded text message.

The bot must support multiple parameters for each command, with certain parameters accessible only to users with specific Discord roles. For example:

- The `digest` command can be called by anyone with the `Everyone` role.
- The `digest` command with the `timeFrame` parameter can only be called by users with the `mod` role.

The project should be structured to facilitate the addition of new Python modules and commands to the command tree easily.

## Objectives

- Create a scalable and modular Discord bot using Python 3.12.
- Implement role-based access control for command parameters.
- Ensure ease of adding new commands and modules over time.
- Adhere to best practices for code structure, security, and performance.

## Functional Requirements

### Commands

1. **`tix` Command**
   - **Description**: Returns an embedded image message.
   - **Usage**: `/tix [parameters]`
   - **Parameters**:
     - To be defined based on future requirements.
   - **Access**: All users.

2. **`digest` Command**
   - **Description**: Returns an embedded text message.
   - **Usage**: `/digest [parameters]`
   - **Parameters**:
     - **`timeFrame`**:
       - **Description**: Specifies the time frame for the digest.
       - **Access**: Only users with the `mod` role.
     - Additional parameters can be added as needed.
   - **Access**:
     - Basic command: Users with the `Everyone` role, which means everyone in the guild.
     - With `timeFrame`: Users with the `mod` role.

### Role-Based Access Control

- Implement checks to verify user roles before executing commands with restricted parameters.
- Define a utility module for role verification to be reused across commands.

### Extensibility

- Design the bot to allow straightforward addition of new commands and parameters.
- Use a modular architecture where each command resides in its own module.
- Implement automatic command registration by scanning the commands directory.

## Non-Functional Requirements

- **Performance**: Commands should execute promptly without noticeable delay.
- **Security**: Safeguard against unauthorized access and handle exceptions gracefully.
- **Maintainability**: Code should be clean, well-documented, and follow PEP 8 standards.
- **Scalability**: Capable of handling additional commands and increased user interaction over time.

## Technical Requirements

- **Programming Language**: Python 3.12
- **Discord Library**: Use a modern, actively maintained library like `discord.py` (ensure compatibility with Python 3.12).
- **Environment**: Run within a virtual environment for dependency management.
- **Version Control**: Use Git for version control with the repository structured as per the guidelines.

## Project Structure

```plaintext
project-root/
├── PRD.md
├── app/
│   ├── bot.py
│   ├── discordbot.py
│   ├── config.py
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── digest.py
│   │   └── tix.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── role_checks.py
│   ├── channels/
│   │   ├── __init__.py
│   │   └── scanner.py
│   ├── dadlan/
│   │   ├── __init__.py
│   │   └── client.py
│   ...
├── pyproject.toml
└── README.md
```

- **`bot.py`**: The main entry point for the bot.
- **`discordbot.py`**: A wrapper class for the Discord bot to speed up command sync.
- **`config.py`**: Configuration for the bot.
- **`commands/`**: Contains individual command modules.
- **`utils/`**: Utility functions such as role verification and error handling.
- **`channels/`**: Channel utilities such as scanning for new channels.
- **`dadlan/`**: A client for the Dadlan API.
- **`summariser/`**: A client for the Summariser API.
- **`pruner/`**: A client for the Pruner API.
- **`pyproject.toml`**: The Python project configuration file.
- **`README.md`**: The project's README file.

## Implementation Details

### Command Modules

- Each command should be a separate module within the `app/commands/` directory.
- Use named exports for command functions.
- Commands should be registered in `app/discordbot.py`.
- When a command is complex or requires a lot of dependencies, supporting functions should be in a separate module, for example `app/pruner/`.

### Role Verification

- Implement a utility function in `utils/role_checks.py` to verify user roles.
- Use decorators to enforce role-based access control on command parameters.

### Error Handling

- Place error handling at the beginning of functions using guard clauses.
- Return user-friendly error messages without exposing sensitive information.
- Log exceptions using the `log.error` method.

### Logging

- Implement logging for command usage, errors, and important events.
- Log exceptions using the `log.error` method.
- Log information using the `log.info` method.
- Log debug information, such as function entry and exit, using the `log.debug` method.
- Create a logger in each module using the `get_logger` function from `dpn_pyutils` called `log` using the module `__name__` as the logger name.

## Security Considerations

- **Token Management**: Assume the Discord bot token is stored securely using environment variables or a `.env` file.
- **Input Validation**: Sanitize all user inputs to prevent injection attacks.
- **Permissions**: Ensure the bot has only the necessary permissions within the guild.


## Documentation

- **Code Documentation**: Include docstrings for all modules, classes, and functions.
- **README.md**: Provide setup instructions, usage examples, and contribution guidelines.
- **In-Line Comments**: Add comments for complex logic or important sections of code.
- **PRD.md**: This document.
- `.cursorrules`: Cursor rules.

## Future Enhancements

- **Additional Commands**: Plan to add more commands as needed by the guild.
- **Database Integration**: If needed, assume integration with a database like PostgreSQL for persistent data storage in the future.

## Dependencies

- **discord.py**: For interacting with the Discord API.
- **Python-dotenv**: For managing environment variables (if needed).
- **Asyncio**: Utilize asynchronous programming for non-blocking operations.
- **dpn_pyutils**: For logging and other utilities.
- **pydantic_settings**: For configuration.
- **pydantic**: For data validation.
