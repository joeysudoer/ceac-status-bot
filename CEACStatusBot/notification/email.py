from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

from CEACStatusBot.utils import log_with_timestamp
from .handle import NotificationHandle

class EmailNotificationHandle(NotificationHandle):
    def __init__(self,fromEmail:str,toEmail:str,emailPassword:str,hostAddress:str='') -> None:
        super().__init__()
        self.__fromEmail = fromEmail
        self.__toEmail = toEmail.split("|")
        self.__emailPassword = emailPassword
        self.__hostAddress = hostAddress or "smtp."+fromEmail.split("@")[1]
        if ':' in self.__hostAddress:
            [addr, port] = self.__hostAddress.split(':')
            self.__hostAddress = addr
            self.__hostPort = int(port)
        else:
            self.__hostPort = 0

    def send(self, result, change_type="status"):
        
        # {'success': True, 'visa_type': 'NONIMMIGRANT VISA APPLICATION', 'status': 'Issued', 'case_created': '30-Aug-2022', 'case_last_updated': '19-Oct-2022', 'description': 'Your visa is in final processing. If you have not received it in more than 10 working days, please see the webpage for contact information of the embassy or consulate where you submitted your application.', 'application_num': '***'}

        if change_type == "case_updated":
            # 仅 case_last_updated 变更，强调美签正在被 Review
            mail_title = f'[CEACStatusBot] 🔍 美签正在被 Review (更新日期: {result["case_last_updated"]})'
        else:
            # status 变更（包括同时变更的情况），强调状态变更
            mail_title = f'[CEACStatusBot] 🇺🇸 美签状态更新: {result["status"]}'
        
        mail_content = str(result)

        msg = MIMEMultipart()
        msg["Subject"] = Header(mail_title,'utf-8')
        msg["From"] = self.__fromEmail
        msg['To'] = ";".join(self.__toEmail)
        msg.attach(MIMEText(mail_content,'plain','utf-8'))

        smtp = SMTP_SSL(self.__hostAddress, self.__hostPort) # ssl登录
        log_with_timestamp(f"Email login result: {smtp.login(self.__fromEmail,self.__emailPassword)}")
        log_with_timestamp(f"Email send result: {smtp.sendmail(self.__fromEmail,self.__toEmail,msg.as_string())}")
        smtp.quit()