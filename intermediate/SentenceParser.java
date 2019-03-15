import java.io.*;
import java.util.*;
import java.text.*;

// Reads a given file of text and creates a new file where each line of the new file is a single sentence from the 
// given file. Removes empty lines.

public class SentenceParser {
	public static void main(String[] args) throws FileNotFoundException, UnsupportedEncodingException {
		String inputFile = "D:/Programming/Github/cse475-sp17/intermediate/sentences/sentences.txt";
		String outputFile = "D:/Programming/Github/cse475-sp17/intermediate/beginner_with_sentences/new.txt";
		PrintWriter writer = new PrintWriter(outputFile, "UTF-8");
		parseData(inputFile, writer);
		writer.close();
	}

	public static void parseData(String filename, PrintWriter writer) {
		BufferedReader reader = null;
		try {
			reader = new BufferedReader(new FileReader(filename));
			String inputLine;
			int line = 0;
			while ((inputLine = reader.readLine()) != null) {
				line++;
				if (inputLine.length() > 0) {
					BreakIterator iterator = BreakIterator.getSentenceInstance(Locale.US);
					iterator.setText(inputLine);
					int start = iterator.first();
					for (int end = iterator.next();	end != BreakIterator.DONE; start = end, end = iterator.next()) {
						writer.println(inputLine.substring(start,end));
					}
				}
			}
			System.out.println("Read " + line + " lines.");
		} catch (IOException e) {
			System.err.println(e.toString());
			e.printStackTrace(System.err);
		} finally {
			if (reader != null) {
				try {
					reader.close();
				} catch (IOException e) {
					System.err.println(e.toString());
					e.printStackTrace(System.err);
				}
			}
		}
	}
}
