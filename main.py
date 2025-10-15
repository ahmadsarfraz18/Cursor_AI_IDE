from agents import Agent, Runner, RunConfig, OpenAIChatCompletionsModel, set_tracing_disabled, function_tool, enable_verbose_stdout_logging
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
set_tracing_disabled(disabled=True)
enable_verbose_stdout_logging()

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set in environment variables. ")

external_client = AsyncOpenAI(
    api_key= gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model= OpenAIChatCompletionsModel(
    model= "gemini-2.5-flash",
    openai_client= external_client
)

config = RunConfig(
    model= model
)


@function_tool(strict_mode=False)
def file_and_folder_handler(
    file_name: str = None,
    folder_name: str = None,
    content: str = None,
    file_path: str = None,
    read: bool = None
):
    try: 
        result_messages= []

        # Create a new folder

        if folder_name:
            os.makedirs(folder_name, exist_ok= True)
            result_messages.append(f"Folder '{folder_name}' is ready. ")

        if read and file_path:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    file_data= f.read()
                result_messages.append(f"Content of {file_path} is {file_data}. ")
        else:
            result_messages.append(f"File {file_path} does not exist. ")
        

        if file_name:
            if folder_name:
                full_path= os.path.join(folder_name, file_name)
            else: 
                full_path = file_name
            
            with open(full_path, 'w') as f:
                f.write(content if content else "")

            result_messages.append(f"File '{full_path}' has been created successfully. ")
            if content: 
                result_messages.append(f"Content written to '{full_path}' ")

        return "\n".join(result_messages)
    


    except Exception as e:
        print(f"Error occurred: {e}")


file_handler_agent = Agent(
    name= "FileHandlerAgent",
    instructions= """you are helpfull file management assistant.You can:
    1. Create folders and files
    2. Write content to files
    3. Read content from files
    4. You should use the tool to perform file and folder operations
    5. Generate HTML, CSS JS code snippets when required
    
    Examples of what you can do:
    - Create a folder named 'my_folder'
    - Inside 'my_folder', create a file named e.g 'index.html' and write a basic
      html boilerplate code in it
    - Read the content of 'my_folder/index.html'
    - Create a file named 'styles.css' and write css code to make the background color""",
    model= model,
    tools=[file_and_folder_handler],
    
)

result= Runner.run_sync(
    starting_agent= file_handler_agent,
    # input= "create three file html css and js in folder named full_stack",
    # input= "create a folder named 'test_folder' and inside it create a file named todo_list.htlm and write a html todo list with 3 items in it. and then read the content of the file and print it. ",
    input= "create a file named index.html with animated todo list with code and also good css styling. ",
    run_config= config
)

print(result.final_output)
