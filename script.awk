BEGIN{
    FS = " "
    RS = "\n"
    filecnt = 0
}

{   
    files[filecnt] = FILENAME
    for(i=1; i<=NF; i++){
        origin_vocab[filecnt "#" $i]++
    }
    filecnt++
}

END{
    for(var in origin_vocab){
        split(var, temp, "#") 
        posting_list[temp[2]] = posting_list[temp[2]]" "files[temp[1]]"#"origin_vocab[var]
        term_freq[temp[2]] += origin_vocab[var]
    }
    
    for(var in posting_list){
        print var,"["term_freq[var]"] : ",posting_list[var]
    }
}
