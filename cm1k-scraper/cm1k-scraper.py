''' DESCRIPTION:
    
    This program is designed to scrape the DOCSIS Status page of 
    a Netgear CM1000 modem to pull the QAM, Upload, and OFDM channel
    status tables. This will allow you to monitor the correctable and
    uncorrectable codewords over time. When data is pulled, this program
    automatically rounds to the nearest 30 minutes. For example, if you run
    at 12:35PM, the timestamp will be 12:30PM. It is recommended to 
    only run this once every 30 minutes. 
    
    The default url, username/password will work for any factory modem.
    Change the output folder under the Settings section, run it,
    and three csv files will be produced for the QAM, OFDM, and Upload
    channels.
    
    INPUT: url | The DocisStatus.asp page of a Netgear 1000 modem
    
    OUTPUT: df_qam_channel_statusl.csv   | QAM channel status table
            df_upload_channel_status.csv | Upload channel status table
            df_ofdm_channel_status.csv   | OFDM channel status table
'''

import requests
import pandas as pd
from os.path import exists
from time import sleep

###################################################
################### Settings ######################
###################################################

url       = 'http://192.168.100.1/DocsisStatus.asp'
user      = 'admin'
pw        = 'admin'
outfolder = "B:\\Data\\cm1k-scraper" # Do not include ending \\

###################################################
#################### Begin ########################
###################################################

attempts = 0
success  = False

# Try to log into the modem at most 10 times.
# Sometimes it fails the first try when logging in.
while attempts <= 10 and success == False:
    attempts += 1
    
    print('Login attempt ' + str(attempts) )
    
    resp = requests.get(url, auth=(user, pw))
    
    # Success code = 200
    if resp.status_code == 200:
        print('Success! Pulling channel status...')

        success = True
        now     = pd.Timestamp.now().round('30min') # Round to the nearest 30 minutes
        i       = 3 # Data ranges from tables 4-6
        
        # Create three DataFrames: QAM, Upload, and OFDM
        df_dict = {'df_qam_channel_status':    pd.DataFrame(),
                   'df_upload_channel_status': pd.DataFrame(),
                   'df_ofdm_channel_status':   pd.DataFrame()
                  }
        
        # Pull each table and save it to a dict with the timestamp
        for df in df_dict:
            i+=1
            
            #Read data from table
            df_dict[df] = pd.read_html(resp.content, header=[0], index_col=[0])[i]
            #df_dict[df] = df_dict[df][df_dict[df]['lock_status'] == 'Locked']
            
            #Add a timestamp
            df_dict[df]['timestamp'] = now
            
            # Convert Power and SNR/MER to int. NOTE: SNR/MER does not exist
            # for upload. The try block takes care of this.
            for col in ['Power', 'SNR / MER']:
                try:
                    df_dict[df][col] = df_dict[df][col].str.extract('(\d+\.\d+)').astype('float')
                except:
                    pass
        
            # Store frequency as an int
            df_dict[df]['Frequency'] = df_dict[df]['Frequency'].str.extract('(\d+)').astype('int')
            
            # Rename columns to be more logical
            df_dict[df] = df_dict[df].rename(columns={'Frequency': 'frequency_hz',
                                                      'Power':     'power_dbmv',
                                                      'SNR / MER': 'snr_mer_db'
                                                     }
                                            )
            
            #Standardize the rest of the index/column names
            df_dict[df].columns    = df_dict[df].columns.str.strip() \
                                                        .str.lower() \
                                                        .str.replace(' ', '_')
                                   
            df_dict[df].index.name = df_dict[df].index.name.strip() \
                                                .lower() \
                                                .replace(' ', '_')
            
            print('Saving ' + df + ' to csv...')
            
            outfile = outfolder + '\\' + df + '.csv'
            
            # Do not add a header if the file exists
            header = False if exists(outfile) else True
                
            df_dict[df].to_csv(outfile, float_format='%.1f', mode='a', header=header)
                
    else:
        print('Fail. Status code: ' + str(resp.status_code) )
        
        sleep(3)
        
print('Done')