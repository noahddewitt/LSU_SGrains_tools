import re

def create_gene_str(gene_str_one, gene_str_two):
    #Turn in to dics to allow matching and use of hets
        gene_dict_one = gene_str_to_dict(gene_str_one) 
        gene_dict_two = gene_str_to_dict(gene_str_two) 

        #Sets don't preserve order. A little hacky.
        search_genes = ["FHB1", "FHB_JT", "H13", "H13B", "BYDV2"]
        search_genes.extend(list(set(gene_dict_one.keys()) - set(search_genes)))
        search_genes.extend(list(set(gene_dict_two.keys()) - set(search_genes)))
        new_gene_str = ""

        for gene in search_genes:
            print("Cur Str:")
            print(new_gene_str)
            print("Gene:")
            gene_one = gene_dict_one.get(gene) or ""
            gene_two = gene_dict_two.get(gene) or ""
            print(gene_one)
            print(gene_two)
            #Move on if neither parent has some form of gene
            if {gene_one, gene_two} != {''}:
                if gene_one != '':
                    gene_one_match = re.search("(HET.*)", gene_one.upper())
                    if gene_one_match is None:
                        gene_class_one = "HOM"
                    else:
                        gene_class_one = gene_one_match.group(1)
                else:
                    gene_class_one = ''

                if gene_two != '':
                    gene_two_match = re.search("(HET.*)", gene_two.upper())
                    if gene_two_match is None:
                        gene_class_two = "HOM"
                    else:
                        gene_class_two = gene_two_match.group(1)
                else:
                    gene_class_two = ''
                
                gene_class_set = {gene_class_one, gene_class_two}
                print("  Gene Clas:")
                print(gene_class_set)
                #Both parents homozygous
                if gene_class_set == {'HOM'}:
                    new_gene = gene
                elif (gene_class_set == {'', 'HOM'} or gene_class_set == {'HET'}):
                    new_gene = gene + "Het" 
                #These classes convey uncertainty. You can't go from uncertain to certain.
                elif (gene_class_set == {'HOM', 'HET'} or gene_class_set == {'HOM', 'HET+'} or
                    gene_class_set == {'HOM', 'HET-'} or gene_class_set == {'HET', 'HET+'}):
                    new_gene = gene + "Het+"
                elif (gene_class_set == {'', 'HET'} or gene_class_set == {'HET', 'HET-'} or 
                    gene_class_set == {'', 'HET+'} or gene_class_set == {'', 'HET-'}):
                    new_gene = gene + "Het-"
                else:
                    print("Classs " + str(gene_class_set) + " unrecognized.")
                new_gene_str += ", " + new_gene

        return(new_gene_str) 

def gene_str_to_dict(gene_str):
    gene_list = re.sub(" ", "", gene_str).split(",")
    gene_list_unique = [re.sub("[Hh][Ee][Tt]\+*\-*$", "", gene).upper() for gene in gene_list]

    gene_dict = {gene_list_unique[i]: gene_list[i] for i in range(len(gene_list))} 

    return(gene_dict)

genestrone = "Fhb1, FHB_JTHet, H13, Sbm1aHet"
genestrtwo = "Fhb_JTHet, H13, Pm1"

print(create_gene_str(genestrone, genestrtwo))
