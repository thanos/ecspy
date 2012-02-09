import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import getpass
import os

class EmailObserver(object):
    def __init__(self, username, password, server, port=587):
        self.username = username
        self.password = password
        self.server = server
        self.port = port
        self.subject = "ECsPy observer report"
        
    def _send_mail(self, fromaddr, toaddr, subject, text, attachments=None):
        msg = MIMEMultipart()
        msg['From'] = "ECsPy"
        msg['To'] = toaddr
        msg['Subject'] = subject
        msg.attach(MIMEText(text))
        part = MIMEBase('application', 'octet-stream')
        if attachments is not None:
            if not isinstance(attachments, (list, tuple)):
                attachments = [attachments]
            for file in attachments:
                part.set_payload(open(file, 'rb').read())
                Encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
                msg.attach(part)
        mail_server = smtplib.SMTP(self.server, self.port)
        mail_server.ehlo()
        mail_server.starttls()
        mail_server.ehlo()
        mail_server.login(self.username, self.password)
        mail_server.sendmail(fromaddr, toaddr, msg.as_string())
        mail_server.quit()
        
    def __call__(self, population, num_generations, num_evaluations, args):
        population = list(population)
        population.sort(reverse=True)
        worst_fit = population[-1].fitness
        best_fit = population[0].fitness

        plen = len(population)
        if plen % 2 == 1:
            med_fit = population[(plen - 1) / 2].fitness
        else:
            med_fit = float(population[plen / 2 - 1].fitness + population[plen / 2].fitness) / 2
        avg_fit = sum([p.fitness for p in population]) / float(plen)
        std_fit = math.sqrt(sum([(p.fitness - avg_fit)**2 for p in population]) / float(plen - 1))
        
        body = 'Generation Evaluation Worst      Best       Median     Average    Std Dev   \n'
        body += '---------- ---------- ---------- ---------- ---------- ---------- ----------\n'
        body += '{0:10} {1:10} {2:10.5} {3:10.5} {4:10.5} {5:10.5} {6:10.5}\n'.format(num_generations, num_evaluations, worst_fit, best_fit, med_fit, avg_fit, std_fit)
        body += '----------------------------------------------------------------------------\n'
        for p in population:
            body += p + '\n'
        body += '----------------------------------------------------------------------------\n'
        files = []
        stats = args.getdefault("statistics_file", None) 
        inds = args.getdefault("individuals_file", None)
        if stats is not None:
            files.append(stats.name)
        if inds is not None:
            files.append(inds.name)
        self._send_mail(self.from_address, self.to_address, self.subject, body, files)
    
    
if __name__ == '__main__':
    import getpass
    usr = raw_input("Enter your username: ")
    pwd = getpass.getpass("Enter your password: ")
    email_observer = EmailObserver(usr, pwd, "my.mail.server")
    email_observer.from_address = "me@here.com"
    email_observer.to_address = "you@there.com"
    

    
    
    
    
    
    
    
    
    