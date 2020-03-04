import os
import pytz
import logging
from datetime import datetime
from engage_scraper.scraper_logics.santamonica_scraper_models import Message, AgendaItem
from .utils import send_mail
from simple_latex import Preamble, Package, Documentclass, Definition, Command, NewCommand, RenewCommand, BeginClass, EndClass, TextClass, Document, SimpleLatexDocument
from google.cloud import storage
logging.basicConfig()
log = logging.getLogger(__name__)

def escape_email(email):
    escaped_email = email.replace("_", "\_")
    return escaped_email

def add_comment(comment, document):
    email_escaped = escape_email(comment.email)
    document.add(Command("item"))
    document.add(Command("textbf", values=["Name: "]))
    document.add(TextClass("{} {}".format(
        comment.first_name, comment.last_name), True))
    document.add(Command("textbf", values=["email: "]))
    document.add(Command("href", values=["mailto:{}".format(email_escaped), email_escaped]))
    document.add(TextClass("", True))
    document.add(Command("textbf", values=["Feedback: "]))
    document.add(TextClass(comment.content if comment.content else "None", True))
    if comment.authcode is None:
        document.add(Command("textit", values=["Email Authenticated"]))
    else:
        document.add(Command("textit", values=["Email Not Authenticated"]))
    return document


def new_mdenv(color, mdenv_value, margins="6pt", roundcorner="4pt"):
    command = Command("newmdenv", parameters={
        "tikzsetting": "{{fill={}, draw=white}}".format(color),
        "innerlinewidth": "1.5pt",
        "roundcorner": roundcorner,
        "innerleftmargin": margins,
        "innerrightmargin": margins,
        "innertopmargin": margins,
        "innerbottommargin": margins
    }, values=[mdenv_value])
    return command


def send_email_pdf(committee, agenda, subtitle_date, file_name, file_path, session):
    email_body = """<html>
        <head>
            <style>
                body {
                    font-family: sans-serif;
                    font-size: 12px;
                    color: #000;
                }
            </style>
        </head>
        <body>
            <p>Greetings from Engage</p>
            <p>Please find attached the latest report for the upcoming Council Meeting.</p>
            <p>Thank you,</p>
            <p>Your Engage team</p>
            <hr>
            <p><i>This is an automated message, for any questions please contact <a hrek=mailto:contact@engage.town?subject=Feedback%20Agenda%20Comments%20Report>contact@engage.town</a></i></p>
        </body
    </html>
    """
    subject = "{} Meeting {} - Agenda Recommendations, Comment Submissions for {}".format(
        committee.name, agenda.meeting_id, subtitle_date)
    send_mail(committee, subject, email_body, file_name, file_path)
    agenda.processed = True
    agenda.pdf_location = f"https://storage.googleapis.com/engagepdfs/{file_name}"
    session.commit()


def write_pdf_for_agenda(committee, agenda, items, session):
    static_root = os.path.join("/", "pdfs")
    tz = pytz.timezone(committee.location_tz)
    datetime_local = datetime.fromtimestamp(
        agenda.cutoff_time).astimezone(tz=tz)
    datetime_process_time = datetime.now().astimezone(tz=tz)
    if not os.path.exists(static_root):
        os.mkdir(static_root)
    file_name_base = "{}_Meeting_{}".format(
        "_".join(committee.name.split(" ")), agenda.meeting_id)
    file_name_tex = file_name_base + ".tex"
    file_name_pdf = file_name_base + ".pdf"
    file_path = os.path.join(static_root, file_name_pdf)
    try:
        sld = SimpleLatexDocument()
        preamble = Preamble()
        document = Document()
        dateformatted = "{} {}, {}".format(datetime_local.strftime("%B"),
                                          datetime_local.day, datetime_local.year)
        title = "Feedback on Items for {} on {}".format(
            committee.name, dateformatted)
        preamble = Preamble(title,
                            "prepared by sm.engage.town",
                            str(datetime_process_time),
                            documentclass=Documentclass("scrbook", {"oneside": None}))

        preamble.add(Package('geometry', {"top": "2.5cm",
                                          "right": "2.5cm",
                                          "bottom": "2.5cm",
                                          "left": "2.5cm"}))
        preamble.add(Package('hyperref', {"pdfpagelayout": "useoutlines",
                                          "bookmarks": None,
                                          "bookmarksopen": "true",
                                          "bookmarksnumbered": "true",
                                          "breaklinks": "true",
                                          "linktocpage": None,
                                          "pagebackref": None,
                                          "colorlinks": "false",
                                          "linkcolor": "blue",
                                          "urlcolor": "blue",
                                          "citecolor": "red",
                                          "anchorcolor": "gren",
                                          "pdftex": None,
                                          "plainpages": "false",
                                          "pdfpagelabels": None,
                                          "hyperindex": "true",
                                          "hyperfigures": None}))

        preamble.add(Package("inputenc", {"utf8": None}))
        preamble.add(Package("tocbibind", {"nottoc": None}))
        preamble.add(Package("setspace"))
        preamble.add(Package("fancyhdr"))
        preamble.add(Package("xcolor"))
        preamble.add(Package("lastpage"))
        preamble.add(Package("titlesec"))
        preamble.add(Package("mdframed", {"framemethod": "tikz"}))
        preamble.add(Command("hypersetup", values=[
                     "colorlinks=false, linktoc=all, linkcolor=black, hidelinks"]))
        preamble.add(Command(command="titleformat",
                             optional="\\chapter",
                             parameters={"display": None},
                             values=["\\normalfont\\huge\\bfseries", "", "0pt", "\\Huge"], escapeValues=False, escapeText=False))
        preamble.add(Command("titlespacing", "\\chapter", values=[
            "0pt", "-30pt", "20pt"], starred=True,escapeValues=False, escapeText=False))
        preamble.add(Command("pagestyle", values=["fancy"]))
        preamble.add(Command("fancyhf", values=[""]))
        preamble.add(RenewCommand("familydefault", "\\sfdefault"))
        preamble.add(RenewCommand(
            "chaptermark", "\\markboth{\\MakeUppercase{#1}}{}", arguments="1"))
        preamble.add(Command("fancyhead", parameters={
            "R": None}, values=["\\leftmark"]))
        preamble.add(Command("fancyhead", parameters={
            "L": None}, values=["\\rightmark"]))
        preamble.add(Command("fancyfoot", parameters={"R": None}, values=[
            "\\thepage \\ of \\pageref{LastPage}"], escapeValues=False, escapeText=False))
        preamble.add(Command("definecolor", values=[
            "blue", "RGB", "225,225,255"]))
        preamble.add(Command("definecolor", values=[
            "white", "RGB", "255,255,255"]))
        preamble.add(Command("definecolor", values=[
            "green", "RGB", "0,150,0"]))
        preamble.add(Command("definecolor", values=[
            "gray", "RGB", "220,220,220"]))
        preamble.add(Command("definecolor", values=[
            "black", "RGB", "0,0,0"]))
        preamble.add(Command("definecolor", values=[
            "red", "RGB", "255,0,0"]))
        preamble.add(new_mdenv("gray", "nocommentsbox"))
        preamble.add(new_mdenv("green", "probox"))
        preamble.add(new_mdenv("red", "conbox"))
        preamble.add(new_mdenv("black", "needbox"))
        preamble.add(Definition("meetingdate", title))
        sld.add(preamble)
        document = Document()
        document.add(Command("maketitle"))
        document.add(Command("thispagestyle", values=["fancy"]))
        document.add(Command("tableofcontents"))
        document.add(Command("thispagestyle", values=["fancy"]))
        for agenda_item in items:
            document.add(Command("chapter", values=[
                         "Agenda Item {}".format(agenda_item.agenda_item_id), agenda_item.title]))
            document.add(Command("thispagestyle", values=["fancy"]))
            messages = session.query(Message).filter(
                Message.agenda_item_id == agenda_item.id)
            pro_comments_on_agenda_item = messages.filter(
                Message.pro == 0).all()
            con_comments_on_agenda_item = messages.filter(
                Message.pro == 1).all()
            need_info_comments_on_agenda_item = messages.filter(
                Message.pro == 2).all()
            if (pro_comments_on_agenda_item or con_comments_on_agenda_item or
                    need_info_comments_on_agenda_item):
                if pro_comments_on_agenda_item:
                    document.add(BeginClass("probox"))
                    document.add(Command("textbf", values=[Command(
                        "color", values=["white"], text="Pro feedback on this item")]))
                    document.add(EndClass("probox"))
                    document.add(BeginClass("enumerate"))
                    for comment in pro_comments_on_agenda_item:
                        document = add_comment(comment, document)
                    document.add(EndClass("enumerate"))
                if con_comments_on_agenda_item:
                    document.add(BeginClass("conbox"))
                    document.add(Command("textbf", values=[Command(
                        "color", values=["white"], text="Con feedback on this item")]))
                    document.add(EndClass("conbox"))
                    document.add(BeginClass("enumerate"))
                    for comment in con_comments_on_agenda_item:
                        document = add_comment(comment, document)
                    document.add(EndClass("enumerate"))
                if need_info_comments_on_agenda_item:
                    document.add(BeginClass("needbox"))
                    document.add(Command("textbf", values=[Command(
                        "color", values=["white"], text="Need more info feedback on this item")]))
                    document.add(EndClass("needbox"))
                    document.add(BeginClass("enumerate"))
                    for comment in need_info_comments_on_agenda_item:
                        document = add_comment(comment, document)
                    document.add(EndClass("enumerate"))
            # exclude section without comments
            else:
                document.add(BeginClass("nocommentsbox"))
                document.add(Command("textbf", values=[Command("color", values=[
                             "black"], text="No feedback received on this issue.")]))
                document.add(EndClass("nocommentsbox"))
        sld.add(document)
        sld.pdf(static_root, file_name_tex, clean_output_directory=True, DEBUG=True)
        # upload file_name_pdf to google bucket
        storage_client = storage.Client()
        bucket = storage_client.bucket('engagepdfs')
        blob = bucket.blob(file_name_pdf)
        blob.upload_from_filename(file_path)
        send_email_pdf(committee, agenda, dateformatted,
                       file_name_pdf, file_path, session)
    except Exception as exc:
        log.error("ERROR HERE: {}".format(str(exc)))
