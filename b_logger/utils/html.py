class HTML:
    style = '''
        <style>
        body {
            font-family: Arial, Helvetica;
            }
        table {
            width: 100%;
            margin-bottom: 20px;
            border: 1px solid #dddddd;
            border-collapse: collapse;
            }
        th, td {
            font-size: 14px;
            text-align: left;
            vertical-align: top;
            padding: 5px;
            border: 1px solid #dddddd;
        }
        th {
            font-size: 16px;
            font-weight: bold;
        }
        .summary-test-block {
            overflow: hidden; 
            white-space: nowrap;
            max-width: 150px;
        }
        .summary-status-block {
            max-width: 10px;
            min-width: 5px;
        }
        .td-test-info {
            max-width: 200px;
            min-width: 200px;
            overflow-wrap: break-word;
            }
        .td-test-steps {
            max-width: 400px;
            min-width: 300px;
            overflow-wrap: break-word;
            }
        .td-test-errors {
            max-width: 700px;
            min-width: 300px;
            overflow-wrap: break-word;
        }
        .td-content {
            font-family: Arial, Helvetica;
            white-space: pre-wrap;
            overflow-wrap: break-word;
            word-wrap: break-word;
        }
        .error-code {
            font-family: Consolas, monospace;
            max-width: 600px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .step-num {
            border-radius: 15%;
            padding: 1px 5px;
            margin-right: 5px;
            margin-bottom: 4px;
            display: inline-block;
        }
        .loan-params {
            font-family: Consolas, monospace;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .module-tr {
            height: 50px;
        }
        .module-td {
            font-size: 16px; 
            font-weight: bold;  
            text-align: center;
            vertical-align: middle;
            background-color: #e7e7e7;
            }
        .background-passed {
            background-color: #2ecc71;
        }
        .background-failed {
            background-color: #e74c3c;
            }
        .background-skipped {
            background-color: #808080;
        }
        .highlight-passed {
            color: #2ecc71; 
            font-weight: bold;
        }
        .highlight-failed {
            color: #e74c3c; 
            font-weight: bold;
        }
        .highlight-skipped {
            color: #808080; 
            font-weight: bold;
        }
        </style>\n'''

    def log_head(self, env, module, mskdt, fldt):
        log_head = (
            f'\n<!-- Log Head Start -->\n\n'
            f'<!DOCTYPE html>\n'
            f'<html>\n'
            f'<head>\n'
            f'<meta charset="UTF-8">\n'
            # f'<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            f'<title>{env} - {module}</title>\n'
            f'{self.style}\n'
            f'</head>\n'
            f'<body>\n'
            f'<p><strong>{env} - {module} - MSK: {mskdt} / FL: {fldt}</strong></p>\n'
            f'\n<!-- Log Head End -->\n\n'
        )
        return log_head

    table_head = (
        '\n<!-- Table Head Start -->\n\n'
        '<table>\n'
        '<thead>\n'
        '<tr>\n'
        '<th>#</th>\n'
        '<th class="td-test-info">Test Info</th>\n'
        '<th class="td-test-steps">Steps</th>\n'
        '<th class="td-test-errors">Errors</th>\n'
        '</tr>\n'
        '</thead>\n'
        '<tbody>\n'
        '\n<!-- Table Head End -->\n\n'
    )

    @staticmethod
    def module_block(module, with_link=False):
        if with_link:
            mb = (f'<tr class="module-tr">'
                  f'<td class="module-td" colspan="5" id="{module}">{module}</td>'
                  f'</tr>\n')
        else:
            mb = (f'<tr class="module-tr">'
                  f'<td class="module-td" colspan="5">{module}</td>'
                  f'</tr>\n')
        return mb

    @staticmethod
    def log_entry(css_class, t_num, test_info, steps, errors, log_id):
        log_entry = (
            f'<tr>\n'
            f'<td class="{css_class}">{t_num}</td>\n'
            f'<td class="td-test-info" id="{log_id}"><pre class="td-content">{test_info}</pre></td>\n'
            f'<td class="td-test-steps"><pre class="td-content">{steps}</pre></td>\n'
            f'<td class="td-test-errors"><pre class="td-content">{errors}</pre></td>\n'
            f'</tr>\n'
        )
        return log_entry
