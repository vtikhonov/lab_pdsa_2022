# Probabilistic data structures and algorithms course lab work

## Tasks

### 1. K-Top frequency with Count-Min Sketch problem implementation
The task was covered in the course and you could find corresponding slides in https://drive.google.com/file/d/1byG7KldSnqnaZLq7zW3kswaAH4zGnNRl/view?usp=sharing under 'Count-Min Sketch' sub section.

The input datasets shall be read as a txt file and the words extracted using " ,.:;!" separators, and some obvious frequent words like articles or pronouns shall be omitted, the application shall use skip_words.txt for such words.

The application shall take next arguments:
* --input PATH: path to file or folder with a textual file
* -k NUMBER: number of top frequent element that we are looking for.
* --parallel <CHUNKS>: (disabled by default) whether parallelized version algorithm is used: the input dataset is split (manually or automatic) into several partitions and multiple count-min sketches are merged at the end. It is expected that the final result is the same
* -m NUM: count-min sketch buffer size
* -p NUM: number of independent hash functions
* -c NUM: number of bits per counter, default is 12
* --hash=HASH_FUNCTION: (optional) to utilize specified hash function, default is the one provided by the programming language: hashCode() for Java, hash() for Python etc

The output shall be a table written into STDOUT or a csv file with top K frequent words in descending order:
| word  | freq_ref | freq_approx | error      |
|-------|----------|-------------|------------|
| hello | 156      | 200         | 100*44/156 |
| world | 145      | 147         | 100*2/145  |
| ...   | ...      | ...         | ...        |


Try to run the algorithm using *p*  and *m* inferred from standard error and epsilon, use δ = 2% and ε = 0.005. Are the results good enough?




### 2. HyperLogLog++ implementation
See corresponding section in the PDSA course slides or any available documentation.

The input datasets shall be read as a txt file and the words extracted using " ,.:;!" separators.

... TBD...

## Notes
* The input datasets can be found at [project Gutenberg library's top 100 EBooks last 30 days](https://www.gutenberg.org/browse/scores/top#books-last30), as the rating is dynamic, see input_datasets.txt file that is a snapshot from the rating as for 2022-04-06. Each student picks a dataset/book according to their `dataset_id` in [the student list](https://docs.google.com/spreadsheets/d/1B5h6lM6geeOALARq5s0G5nL6MUmSNmSr4P07yjMYY7w/edit?usp=sharing).
* The student work shall be committed as a separate branch, and PR later will be processed by the teacher, so please put all your code/artifacts into a folder with your full_name
* The programming language choice is completely up to you, but please don't pick an esolang, spare your teacher's nerves :)
* The IDE is also completely your choice, I ask you to not publish IDE specific files, but rely on a widely used build system. For example, if your preferred IDE is the Intellij Idea, you better implement your project with [maven](https://maven.apache.org/) build system, which is natively supported by majority of IDEs for java including the Intellij. And it would be much easier to check how your application runs on a new workstation.
* [No need to publish compiled binaries to git](https://vegeta2102.medium.com/why-you-should-not-push-binary-files-to-git-and-what-to-do-if-you-do-29f34692cef0)
* Please provide a requirements section in the Readme file, specifying which tools are needed to run your app, e.g. 'java 8 + mvn 3.0.3' or 'python 3.8.6 + pip 20.2.1'
* Use efficient datastructures, e.g. if a theory claims that the structure takes `m * p bits`, it shall be kept, sure programming language overhead is inevitable.
* The result shall be deterministic, i.e. any involved pseudo-randomness shall be manageable - use predefined/hardcoded seeds. If sorting is needed, use a stable version.
* Covering the code with unittest is a big plus
* If your application building/running requires any special steps, please mention it a readme-like file. Ideally it would be some `run.sh` script that compiles (if needed) and runs the app with all the arguments like `run.sh --input mybook.txt -k 20 -p 7 -m 512`
