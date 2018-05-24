BEGIN{
    FS = " "
    RS = "\n"
    filecnt = 0
}

{   
    if ($1 == "<DOCNO>"){
        doc++
        docno[doc] = $2
    }else{
        for(i=1; i<=NF; i++){
            origin_vocab[doc "#" $i]++
        }
    }
}

END{
    for(var in origin_vocab){
        split(var, temp, "#") 
        posting_list[temp[2]] = posting_list[temp[2]]" "docno[temp[1]]"#"origin_vocab[var]
        term_freq[temp[2]] += origin_vocab[var]
    }
    
    for(var in posting_list){
        print var,"["term_freq[var]"] : ",posting_list[var]
    }
}
