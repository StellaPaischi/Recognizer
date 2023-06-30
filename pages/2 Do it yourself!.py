import streamlit as st
import os
import VoiceChoice as vc
from keras.models import Sequential, load_model
from keras.layers  import Dense, LSTM, Dropout
from keras.callbacks import ModelCheckpoint, TensorBoard, EarlyStopping
from sklearn.preprocessing import StandardScaler
import pandas as pd
from sklearn.model_selection import train_test_split
from keras.optimizers import Adam

import base64



model_file_path = 'my_model.h5'



def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{file_label}">Download {file_label}</a>'
    return href





def upload_and_convert_newPath(new_path):
    uploaded_file2 = st.file_uploader("Wählen Sie eine Datei zum Hochladen aus", type=["mp4", "wav"], key="file_uploader2")
    if uploaded_file2 is not None:
        file_details = {"FileName":uploaded_file2.name,"FileType":uploaded_file2.type}
        st.write(file_details)
        with open(os.path.join(new_path,uploaded_file2.name),"wb") as f:
            f.write(uploaded_file2.getbuffer())
        if uploaded_file2.type == "video/mp4":
            vc.mp4_to_wav(uploaded_file2,vc.get_current_date_time() + ".wav")
            return True
        else:
            st.success("Hochgeladene Datei ist bereits im WAV-Format")
            return True

def neuronal_network(excel_file_train_data,excel_file_test_data, layers = 0, neurons=0 ):
                
                # if layers != 0 and neurons != 0:
                #     if layers > len(neurons):
                #         raise   ValueError("Layer Size is bigger then neurons array size")
                #     elif layers < len(neurons):
                #         raise ValueError("Neurons array size is bigger then layer size")
                
                vc.delete_first_column_excel(excel_file_test_data)
                # add_id_column(excelFile)
                data = pd.read_excel(excel_file_train_data)
                data2 = pd.read_excel(excel_file_test_data)
                # data2 = data2.drop(["Unnamed: 0"], axis=1)
                st.write(data2)
                
                data = data.dropna()
                scaler = StandardScaler()
                # scaler2 = StandardScaler()
                X_data = data.drop(["label"],axis=1)
                X_data2 = data2.drop(["label"],axis=1)
                scaler = scaler.fit(X_data)
                X_scaler_data = scaler.transform(X_data)
                X2_scaler2_data = scaler.transform(X_data2)
                # st.write(X_scaler_data)
                # st.write(X2_scaler2_data)
                y1 = data["label"]
                y2 = data2["label"]

                X_train, X_test, y_train, y_test = train_test_split(X_scaler_data, y1, test_size=0.2)
                model = Sequential()
                # model.add(Dense(64, activation='relu'))
                # model.add(Dense(32, activation='relu'))
                # model.add(Dense(16, activation='relu'))
                # model.add(Dense(8, activation='relu'))
       
                for i in range(layers):
                    model.add(Dense(neurons[i], activation='relu'))

                model.add(Dense(1, activation='sigmoid'))
                optimizer = Adam(learning_rate=0.002)
                model.compile(loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])

                early_stopping = EarlyStopping(monitor='val_loss', patience=10)

                history = model.fit(X_train, y_train, epochs=1000, batch_size=32,
                                validation_data=(X_test, y_test), callbacks=[early_stopping])
        
                y_pred = model.predict(X2_scaler2_data)
                y_pred = (y_pred > 0.5).astype(int)
                
                acc = history.history['accuracy']
                val_acc = history.history['val_accuracy']
                
                global m;
                global f;

                st.write(y_pred)
                countZero = 0 
                countOne = 0
                for i in y_pred:
                    if(i == 0):
                        countZero = countZero + 1
                        m += 1
                    else:
                        countOne = countOne + 1
                        f += 1
                if(countZero > countOne):
                    
                    st.write("Auf der gesprochenen Audiodatei spricht wahrscheinlich ein Mann!")
                    
                elif(countOne > countZero):
                    st.write("Auf der gesprochenen Audiodatei spricht wahrscheinlich eine Frau!")
                                    
                model.save('my_model.h5')
                return acc, val_acc





m = 0
f = 0


if upload_and_convert_newPath("tempDir2") == True:

    max_layers = 5
    layer_options = list(range(1, max_layers + 1))

    if 'num_layers' not in st.session_state:
        st.session_state.num_layers = layer_options[0]

    num_layers = st.selectbox("Select number of layers", layer_options, key='num_layers')

    neurons = []
    for i in range(num_layers):
        if f'neurons_{i}' not in st.session_state:
            st.session_state[f'neurons_{i}'] = 16
        n = st.number_input(f"Select number of neurons in layer {i + 1}", min_value=1, value=st.session_state[f'neurons_{i}'], key=f'neurons_{i}')
        neurons.append(n)

    st.write(f"Anzahl der Layers: {num_layers}")
    st.write(f"Anzahl der Neuronen in jedem Layer: {neurons}")
    if st.button('Start'):
            for file in os.listdir("tempDir2/"):
                 if file.endswith(".wav"):
                    excelFile = vc.get_single_excel_with_features_no_label(f"tempDir2/{file}",f"tempDir2/{file}",10,True)
                    val_acc = neuronal_network("TrainDataFuerNeuronalesNetzohneGroupID.xlsx",excelFile,num_layers,neurons)
                    os.remove(f"{excelFile}")
                    val_acc = val_acc[len(val_acc) - 1]
                    st.write(f"Die Validierungsgenauigkeit deines Modells entsprich {val_acc}, diese kann stimmen muss sie aber nicht, denn abhängig von Tonqualität, Tonstärken der Audiodatei und Tonklang der Person kann die Vorhersage dennoch Falsch sein!")
                    
                    st.balloons()
                    os.remove(f"tempDir2/{file}")
                    st.markdown(get_binary_file_downloader_html(model_file_path, 'my_model.h5'), unsafe_allow_html=True)