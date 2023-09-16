import pandas as pd
import xml.etree.ElementTree as ET 


def parse_sra(path):
    # analyze xml
    tree = ET.parse(path) 
    # get as xml
    root = tree.getroot()
    # get the xml data
    li_result = []
    for childs in root:
        # EXPERIMENT tag
        li_experiment = {}
        for child in childs:
            # experiment info
            if child.tag == 'EXPERIMENT':
                li_experiment['EXPERIMENT'] = child.attrib['accession']
                for i in child.iter():
                    if i.tag == 'STUDY_REF':
                        li_experiment['STUDY_REF'] = i.attrib['accession']
                    if i.tag == 'DESIGN':
                        for j in i.iter():
                            if j.tag == 'SAMPLE_DESCRIPTOR':
                                li_experiment['SAMPLE_DESCRIPTOR'] = j.attrib['accession']
                            if j.tag == 'LIBRARY_STRATEGY':
                                li_experiment['LIBRARY_STRATEGY'] = j.text
                            if j.tag == 'LIBRARY_SOURCE':
                                li_experiment['LIBRARY_SOURCE'] = j.text
                            if j.tag == 'LIBRARY_SELECTION':
                                li_experiment['LIBRARY_SELECTION'] = j.text
                            if j.tag == 'PAIRED':
                                li_experiment['LIBRARY_LAYOUT'] = 'PAIRED'
                            elif j.tag == 'SINGLE':
                                li_experiment['LIBRARY_LAYOUT'] = 'SINGLE'
                    if i.tag == 'INSTRUMENT_MODEL':
                        li_experiment['INSTRUMENT_MODEL'] = i.text
            # study info
            if child.tag == 'STUDY':
                for i in child.iter():
                    if i.tag == 'STUDY_TITLE':
                        li_experiment['STUDY_TITLE'] = i.text
            # sample info
            if child.tag == 'SAMPLE':
                for i in child.iter():
                    if i.tag == 'TITLE':
                        li_experiment['TITLE'] = i.text
                    # print(ch.tag)
                    if i.tag == 'SCIENTIFIC_NAME':
                        li_experiment['SCIENTIFIC_NAME'] = i.text
                    if i.tag == 'SAMPLE_ATTRIBUTES':
                        for j in i.iter():
                            if j.tag == 'TAG':
                                tag = j.text
                            if j.tag == 'VALUE':
                                value = j.text
                                li_experiment[tag] = value
            # run info
            if child.tag == 'RUN_SET':
                li_experiment['RUNS'] = child.attrib['runs']
                li_experiment['BASES'] = child.attrib['bases']
                li_experiment['SPOTS'] = child.attrib['spots']
                # SRR
                for i in child.iter():
                    if i.tag == 'RUN':
                        li_experiment['RUN'] = i.attrib['accession']
        li_result.append(li_experiment)
    df = pd.DataFrame(li_result)
    return df


import PySimpleGUI as sg
sg.theme('Default')
frame1 = sg.Frame('',
                  [
                      [
                          sg.Text('Choose .xml file', font=('Arial', 12))
                      ],
                      [
                          sg.Text('Input File'),
                          sg.InputText('Select file', key='-INPUTTEXT-', enable_events=True,size=(20)),
                          sg.FileBrowse(button_text='Brouse', font=('Arial',10), key='-FILENAME-',
                                        file_types = (("Text files", "*.xml")))
                      ],
                      [
                          sg.Text('Output format :'),
                          sg.Radio('.tsv', group_id='g1', key='type_tsv'), sg.Radio('.csv', group_id='g1', key='type_csv'), sg.Radio('.xlsx', group_id='g1', key='type_xlsx')
                      ],
                      [
                          sg.Text('Save File'),
                          sg.InputText('Select file', enable_events=True,size=(20), key='-SAVE_PATH-',readonly=True),
                          # save_path2からeventでvalueを取得できない?
                          sg.FileSaveAs(button_text='Brouse', font=('Arial',10), key='-SAVE_PATH2-', enable_events=True),
                          sg.Push()
                      ],
                      [
                          sg.Push(),
                          sg.Button(button_text='Execute', font=('Arial', 10), size=(10), key='-EXECUTE-', enable_events=True),
                          sg.Push()
                      ]
                  ], size=(260, 140)
                  )
layout = [
    [
        frame1,
        # frame2
    ]
]
window = sg.Window('SRA Full xml parse', layout, resizable=True)

while True:
    event, values = window.read()

    if event is None:
        print('exit')
        break
    if values['-FILENAME-'] != '':
        xml_path = values['-FILENAME-']
    # if event == '-SAVE_PATH-':
    if values['-SAVE_PATH-']:
        save_path = values['-SAVE_PATH-']
        save_path = ''.join(save_path.split('.')[-1])
        
    if event == '-EXECUTE-':
        try:
            if save_path != '':
                df = parse_sra(xml_path)
            else:
                sg.Popup('Select output file name.')
        except:
            pass
            error_massage = values['-FILENAME-'] + '\n' + 'can\'t open xml file'
            sg.Popup(error_massage)
            
        try:
            if values['type_tsv']:
                save_path = save_path + '.tsv'
                df.to_csv(save_path, sep='\t', index=None)
                sg.Popup('Done')
            elif values['type_csv']:
                save_path = save_path + '.csv'
                df.to_csv(save_path, sep=',', index=None)
                sg.Popup('Done')
            elif values['type_xlsx']:
                save_path = save_path + '.xlsx'
                df.to_excel(save_path, index=None)
                sg.Popup('Done')
            else:
                sg.Popup('Select output file type.')
        except:
            pass
window.close()