# Probabilistic data structures and algorithms course lab work


### Run project instructions 

1. cd in module revutska-anastasiia:
    ```
    $ cd lab_pdsa_2022/revutska-anastasiia
    ```

2. Build jar
    ```
    $ mvn clean install
    ```

3. Check current directory whether target folder was generated
    ```
    $ ls
    
    # should output smth like:
    # pom.xml                src                     target
    ```
4. Run program
    ```
    # with default params
    $ java -jar target/com.revutska-1.0-SNAPSHOT-jar-with-dependencies.jar
    
    # with custom params using -D
    $ java -Dc=32 -Dp=10 -Dinput=qwerty.txt -jar target/com.revutska-1.0-SNAPSHOT-jar-with-dependencies.jar
    ```