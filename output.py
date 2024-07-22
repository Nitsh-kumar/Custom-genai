#import standard libraries
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, AgGridTheme

#import local files
from generate import generate_response
from database import read_sql_query


user_icon = 'icon.png'
assistant_icon = 'ai.jpg'

def show_output(st , question):
        #load all the stored chat history
        if len(st.session_state.messages) > 0:
            for message in st.session_state.messages:
                role = message['role']
                avatar = message.get('avatar', assistant_icon if role == 'assistant' else user_icon)
                if message.get('data') == None:
                    response_df = pd.DataFrame()
                else:
                    response_df = pd.DataFrame(message['data'])
                show_assistant_message(st ,  response_md = message['content']  , response_df = response_df) 
        st.session_state.messages.append({'role': 'user', 'content': question, 'avatar': user_icon})
        with st.chat_message('user', avatar=user_icon):
            st.markdown(question)   
        response_df = pd.DataFrame() 
        response_md =  generate_response(question)
        #if we did'nt get get select query in response text then we will fetch data
        if not response_md.strip().lower().startswith("select"):
            message = {'role': "assistant", 'content': response_md }
            st.session_state.messages.append(message)
            with st.chat_message("assistant", avatar= assistant_icon):
                st.markdown(message['content'])
                exit()
        else:
        # Generate AI response
            try:
                query_result, column_names  = read_sql_query(response_md)
                response_df = pd.DataFrame(query_result, columns=column_names)
            except Exception as e:
                error = str(e)
                message = {'role': "assistant", 'content': error}
                st.session_state.messages.append(message['content'])
                show_assistant_message(st ,  response_md = error) 
                exit()
        # Add AI message to chat history with DataFrame if available
        message = {'role': "assistant", 'content': response_md}
        if not response_df.empty:
            message['data'] = response_df.to_dict()  # Convert DataFrame to dict for storage
        st.session_state.messages.append(message)
        show_assistant_message(st ,  response_md  , response_df) 
        # Display AI message in chat
def show_assistant_message( st , response_md , response_df = pd.DataFrame() ): 
        with st.chat_message("assistant", avatar = assistant_icon):
            if not response_df.empty:
                tab1, tab2 = st.tabs(["Tabular Data", "Graphical Representation"])
                with tab1:
                    # Configure AgGrid options
                    gb = GridOptionsBuilder.from_dataframe(response_df)
                    gb.configure_pagination(paginationPageSize=10)
                    gb.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True, filter=True)
                    grid_options = gb.build()
                    grid_response = AgGrid(
                        response_df,
                        gridOptions=grid_options,
                        enable_enterprise_modules=True,
                        theme=AgGridTheme.STREAMLIT,
                        fit_columns_on_grid_load=True,
                        update_mode='MODEL_CHANGED'
                    )

                    del gb 
                    paginated_data = pd.DataFrame(grid_response['data'])
                with tab2:
                    if len(paginated_data.columns) == 2 and paginated_data.dtypes[1] in ['int64', 'float64']:
                        st.bar_chart(data=paginated_data.set_index(paginated_data.columns[0]))
                    else:
                        st.write("The data is not suitable for a Bar chart.")
            else:
                st.markdown(response_md)