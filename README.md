# Protein_Conformational_Ensembles_Prediction
AlphaFold Architecture-Based Protein Conformational Ensembles Prediction

This is my final year research implementation. The goal of the research is to design and implement a novel pipeline to predict multiple protein conformational ensembles. This novel pipeline is inspired by existing protein structure prediction systems such as AlphaFold2, AFsample, AFsample2, and AFcluster. 

## Data

## running the pipeline

You will need a machine running Linux, AlphaFold does not support other
operating systems. Full installation requires up to 3 TB of disk space to keep
genetic databases (SSD storage is recommended) and a modern NVIDIA GPU (GPUs
with more memory can predict larger protein structures).



### Genetic databases

This step requires `aria2c` to be installed on your machine.

AlphaFold needs multiple genetic (sequence) databases to run:

*   [BFD](https://bfd.mmseqs.com/),
*   [MGnify](https://www.ebi.ac.uk/metagenomics/),
*   [PDB70](http://wwwuser.gwdg.de/~compbiol/data/hhsuite/databases/hhsuite_dbs/),
*   [PDB](https://www.rcsb.org/) (structures in the mmCIF format),
*   [PDB seqres](https://www.rcsb.org/) – only for AlphaFold-Multimer,
*   [UniRef30 (FKA UniClust30)](https://uniclust.mmseqs.com/),
*   [UniProt](https://www.uniprot.org/uniprot/) – only for AlphaFold-Multimer,
*   [UniRef90](https://www.uniprot.org/help/uniref).



### Model parameters

While the AlphaFold code is licensed under the Apache 2.0 License, the AlphaFold
parameters and CASP15 prediction data are made available under the terms of the
CC BY 4.0 license. Please see the [Disclaimer](#license-and-disclaimer) below
for more detail.

The AlphaFold parameters are available from
https://storage.googleapis.com/alphafold/alphafold_params_2022-12-06.tar, and
are downloaded as part of the `scripts/download_all_data.sh` script. This script
will download parameters for:

*   5 models which were used during CASP14, and were extensively validated for
    structure prediction quality (see Jumper et al. 2021, Suppl. Methods 1.12
    for details).
*   5 pTM models, which were fine-tuned to produce pTM (predicted TM-score) and
    (PAE) predicted aligned error values alongside their structure predictions
    (see Jumper et al. 2021, Suppl. Methods 1.9.7 for details).
*   5 AlphaFold-Multimer models that produce pTM and PAE values alongside their
    structure predictions.


