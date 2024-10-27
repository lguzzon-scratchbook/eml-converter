import os
import argparse
from file_operations import extract_email_content, save_all_emails_to_one_file
from html_conversion import convert_to_markdown, convert_to_pdf, convert_to_text, convert_to_json

def main():
    parser = argparse.ArgumentParser(description="Convert .eml files to various formats.")
    parser.add_argument('--input-dir', type=str, required=True, help='Directory with .eml files')
    parser.add_argument('--output-format', type=str, choices=['html', 'pdf', 'markdown', 'txt', 'json'], required=True, help='Format to convert to')
    parser.add_argument('--output-dir', type=str, default='./output', help='Directory to save converted files')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # Example: Loop through EML files in input directory and process them
    for filename in os.listdir(args.input_dir):
        if filename.endswith(".eml"):
            filepath = os.path.join(args.input_dir, filename)
            date, email_content, subject, reply_count = extract_email_content(filepath)
            output_file = os.path.join(args.output_dir, os.path.splitext(filename)[0])

            if args.output_format == "html":
                save_all_emails_to_one_file([(date, filename, email_content, subject, reply_count)], output_file + ".html")
            elif args.output_format == "markdown":
                convert_to_markdown(output_file + ".html", output_file + ".md")
            elif args.output_format == "pdf":
                convert_to_pdf(output_file + ".html", output_file + ".pdf")
            elif args.output_format == "txt":
                convert_to_text(output_file + ".html", output_file + ".txt")
            elif args.output_format == "json":
                convert_to_json(output_file + ".html", output_file + ".json")

if __name__ == "__main__":
    main()