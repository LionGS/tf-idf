import math
import stemmer
import sqlite3

class TF_IDF:
	def __init__(self):
		self.porter = stemmer.Stemmer()

	def DB_build(self, post_list_path):
		self.param = {"idf_N":0, "icf_N":0,}

		self.conn = sqlite3.connect("tfidf.db")
		cur = self.conn.cursor()
		def file_to_dict(file_path):
			temp_post_list = {} # term->{'docs':{doc_name:term_freq}, 'doc_freq':int}
			col_N = 0
			doc_N = 0
			with open(file_path) as f:
				for line in f:
					w2d = line.replace("\n", "").strip().split(":")
					term, docs = w2d[0].strip().split(), w2d[1].strip().split()
					col_freq = int(term[1].replace("[", "").replace("]", ""))
					col_N += col_freq
					temp_post_list[term[0]] = {"col_freq":col_freq, "docs":{}} #
					for doc in docs:
						fnp = doc.split("#")
						f_path, term_freq = fnp[0], int(fnp[1])
						temp_post_list[term[0]]["docs"][f_path] = term_freq
					doc_freq = len(temp_post_list[term[0]]["docs"].items())
					temp_post_list[term[0]]["doc_freq"] = doc_freq
					doc_N += doc_freq
			return temp_post_list, col_N, doc_N

			self.posting_list, self.param["icf_N"], self.param["idf_N"] = file_to_dict(post_list_path)
			cur.execute("INSERT INTO META(idf, icf) VALUES(?,?)", (self.param["idf_N"], self.param["icf_N"]))

			term_addr = "INSERT INTO TERMS(term, doc_freq, col_freq) VALUES(?, ?, ?)"
			doc_addr = "INSERT INTO DOCS(term, doc_id, freq) VALUES(?, ?, ?)"

			for term in self.posting_list:
				docs = self.posting_list[term]["docs"]
				doc_freq = self.posting_list[term]["doc_freq"]
				col_freq = self.posting_list[term]["col_freq"]
				cur.execute(term_addr, (term, doc_freq, col_freq))
				for doc_id in docs:
					cur.execute(doc_addr, (term, doc_id, docs[doc_id]))
			self.conn.commit();
			self.conn.close();


	def word_tf(self, term_freq):
		return 1+math.log(term_freq*1.0)

	def word_idf(self, idf, term_doc_freq):
		return math.log(idf*1.0/term_doc_freq)

	def calc_sent_tfidf(self, sentence):
		self.conn = sqlite3.connect("tfidf.db")
		cur = self.conn.cursor()
		cur.execute("SELECT * FROM META")
		idf_N = cur.fetchall()[0][0]

		doc_finder = "SELECT * FROM DOCS WHERE term=?"
		term_finder = "SELECT * FROM TERMS WHERE term=?"
		query = sentence.strip().split()
		score_lst = {} # doc_id -> score
		for term in query:
			cur.execute(doc_finder, (term,))
			docs = cur.fetchall()
			if len(docs) == 0:
				continue
			cur.execute(term_finder, (term,))
			term_doc_freq = cur.fetchall()[0][1]



			for doc in docs:
				doc_id = doc[1]
				term_freq = doc[2]
				if doc_id in score_lst:
					score_lst[doc_id] += self.word_tf(term_freq)*self.word_idf(idf_N, term_doc_freq)
				else:
					score_lst[doc_id] = self.word_tf(term_freq)*self.word_idf(idf_N, term_doc_freq)
		self.conn.close();
		return score_lst

	def print_sorted_tfidf(self, sentence):
		porter = stemmer.Stemmer()
		stemed_sentence = []
		for word in porter.remove_symbol(sentence.lower()).replace("\n","").split():
			stemed_sentence.append(porter.stem(word,0,len(word)-1))
		stemed_sentence = " ".join(stemed_sentence)

		sc_lst = self.calc_sent_tfidf(stemed_sentence)
		sc_lst = sorted(sc_lst.items(), key=(lambda x:x[1]), reverse=True)

		print "="*50
		print "input query: %s\n"%sentence
		print "stemed query: %s\n"%stemed_sentence
		print " [doc_path | tf-idf]"
		for doc, score in sc_lst[:5]:
			print " [%s | %f]"%(doc, score)

	def save_sorted_tfidf(self, save_path, query_file):
		save = open(save_path, 'w')
		start = 202
		querys = open(query_file)
		for query in querys:
			temp_query = []
			temp = self.porter.remove_symbol(query.lower()).replace("\n","").replace("\r", "").split()
			for word in temp:
				temp_query.append(self.porter.stem(word, 0, len(word)-1))
			temp_query = " ".join(temp_query)

			sc_lst = self.calc_sent_tfidf(temp_query)
			sc_lst = sorted(sc_lst.items(), key=(lambda x:x[1]), reverse=True)

			for i, (doc, score) in enumerate(sc_lst[:1000]):
				save.write("%d Q%d %s %d %f %s\n"%(start, start-1, doc, i+1, score, "geun-sik"))
			start += 1
		save.close()
		querys.close();


	def search(self, sent):
		sentence = []
		for word in self.porter.remove_symbol(sent.lower()).replace("\n", "").split():
			sentence.append(self.porter.stem(word, 0, len(word)-1))
		sentence = " ".join(sentence)
		sc_lst = self.calc_sent_tfidf(sentence)
		sc_lst = sorted(sc_lst.items(), key=(lambda x:x[1]), reverse=True)

		return sc_lst

if __name__ == "__main__":
	scorer = TF_IDF()
	scorer.DB_build("./awked_AP88s.txt")
	query = "No, that would be too easy. Well, we`ll just see how he feels after I..."
	query = "overthrown South Vietnamese government have been released"


	scorer.print_sorted_tfidf(query)
	#scorer.save_sorted_tfidf("AP88_result.txt", "topics.202-250.txt")
	print(scorer.search("overthrown South Vietnamese"))
