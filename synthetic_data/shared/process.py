def get_codings(codings_file):
    import pandas as pd
    codingDF = pd.read_csv(codings_file)
    coding = codingDF['coding'].values.tolist()
    display = codingDF['display'].values.tolist()
    guide_text = codingDF['guide_text'].values.tolist()
    return coding, display, guide_text

def process(codings_file: str, input_dir: str, output_dir: str):
    import glob
    import pandas as pd
    import os
    import json

    # Get the csv files from the input directory
    files = glob.glob(input_dir + "/*.csv")

    # Read codings file
    coding, display, guide_text = get_codings(codings_file)

    # Columns for ouput dataframe
    columns = ['obsTime', 'Temperature', 'normTime', 'coding', 'display', 'value', 'observation']

    for filename in files:
            _, tail = os.path.split(filename)
    
            # Processed filename
            processedFile = os.path.join(output_dir, tail)

            # Processed Dataframe
            processedDF = pd.DataFrame(columns = columns)

            # reading content of csv files
            df = pd.read_csv(filename)

            # File should only contain 1 temperature
            event_temperature = df.loc[0]['Temperature']

            for row in df.itertuples():
                code = row.coding
                coding_index = coding.index(code)
      
                display1 = None
                obsJSON = None
                value = -1
      
                normTime = row.normTime
                obsTime = row.obsTime
                obs = row.observation

                try:
                    # Parse text to generate tabular data
                    obsJSON = json.loads(obs.replace("\'", "\""))

                    if "{'<duration>':" in guide_text[coding_index]:
                        if 'valuePeriod' in obsJSON:
                            value = obsJSON['valuePeriod']['<duration>']
                    elif "'component': [" in guide_text[coding_index]:
                            display1 = display[coding_index]
                    elif 'valueQuantity' in obsJSON:
                            value = obsJSON['valueQuantity']['value']
                    else:
                            print('Cannot get value from: ' + obs)
                except:
                    print('Error parsing: ' + obs)

                if display1 is None:
                    processedDF.loc[len(processedDF.index)] = [obsTime, event_temperature, normTime, code, display[coding_index], value, obs]
                else:
                    if 'component' in obsJSON:
                        component = obsJSON['component']
                  
                        for compJSON in component:
                            display2 = display1 + " - " + compJSON['display']
                
                            if 'valueQuantity' in compJSON: 
                                value = compJSON['valueQuantity']['value']
                            processedDF.loc[len(processedDF.index)] = [obsTime, event_temperature, normTime, code, display2, value, obs]
            try:
                processedDF.to_csv(processedFile, index=False)
                os.remove(filename)
                print(processedFile + " is ready to be transferred for evaluation")
            except:
                print(processedFile + " failed to be converted")