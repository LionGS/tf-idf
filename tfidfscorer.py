import math

class TF_IDF:
    def __init__(self, post_list_path):
        self.param = {"idf_N":0, "icf_N":0,}
        
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
        
    def word_tf(self, term, doc_name):
        return 1+math.log(self.posting_list[term]['docs'][doc_name]*1.0)
        
    def word_idf(self, term):
        return math.log(self.param["idf_N"]*1.0/self.posting_list[term]["doc_freq"])
        
    def calc_sent_tfidf(self, sentence):
        query = sentence.strip().split()
        score_lst = {} # doc_id -> score
        for term in query:
            if term in self.posting_list:
                for doc in self.posting_list[term]['docs']:
                    if doc in score_lst:
                        score_lst[doc] += self.word_tf(term, doc)*self.word_idf(term)
                    else:
                        score_lst[doc] = self.word_tf(term, doc)*self.word_idf(term)
        return score_lst
        
    def print_sorted_tfidf(self, sentence):
        sc_lst = self.calc_sent_tfidf(sentence)
        sc_lst = sorted(sc_lst.items(), key=(lambda x:x[1]), reverse=True)
        
        print "="*50
        print "input query: %s\n"%sentence
        print " [doc_path | tf-idf]"
        for doc, score in sc_lst:
            print " [%s | %f]"%(doc, score)
            print "   ",open(doc).read()

if __name__ == "__main__":
    scorer = TF_IDF("./post.list")
    
    scorer.print_sorted_tfidf("No, that would be too easy. Well, we`ll just see how he feels after I...")
    
    