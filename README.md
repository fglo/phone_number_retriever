# Phone Number Retriever

## ENG:

### Applied criterion for selecting subpages to visit:

1. Program checks if the normalized link text is in an arbitrarily specified list (the list contains words like "contact", "company", "about us", etc.) and take only those that are there,
2. It sorts the retrieved and filtered links according to the order in which their text corresponds to the order of the words in the aforementioned list (I want the "contact" page to be checked first, and only after that, possibly, the "about us" page).

### The criterion used to evaluate the "mainness" of the downloaded numbers:

1. Program checks the text downloaded along with the phone, treating it as a headline of sorts, and looks to see if the word "office" or "reception" in different languages is present
2. If none of these words are found, it downloads the first of the numbers found, which is a landline
3. If no landline is found it retrieves the first number in the list.

### What could be improved:

1. Improve the way phone numbers are found in the page content - the phonenumbers package does not handle some number formats),
2. Use some technology (e.g. selenium) to render the part of the pages that JavaScript is responsible for (to mimic this a bit my solution looks for numbers not only 3. In the page text, but also in the scripts),
4. Retrieve links also from JavaScript (e.g. from instructions such as window.location.href="www.example.com")

Translated with www.DeepL.com/Translator (free version)

## PL:

### Zastosowane kryterium wyboru podstron do odwiedzenia:

1. Sprawdzam czy znormalizowany tekst linku jest w arbitralnie określonej liście (lista zawiera słowa typu "kontakt", "contact", "firma" itp.) i biorę tylko te, które tam są,
2. Sortuję pobrane i odfiltrowane linki według kolejności w jakich ich tekst koresponduje z kolejnością słów we wspomnianej wyżej liście (chcę, aby najpierw sprawdzona została strona "kontakt", a dopiero po niej ewentualnie "o nas").
 
### Zastosowane kryterium oceny "główności" pobranych numerów:

1. Sprawdzam pobrany razem z telefonem tekst, traktując go jak pewnego rodzaju nagłówek i patrzę, czy nie ma w nim słowa "biuro" lub "recepcja" w różnych językach
2. Jeśli żadne z tych słów nie zostało znalezione, to pobieram pierwszy ze znalezionych numerów, który jest linią stacjonarną
3. Jeśli żadna linia stacjonarna nie zostanie znaleziona pobieram pierwszy numer z listy.
 
### Co można poprawić:

1. Usprawnić sposób odnajdywania numerów telefonów w zawartości strony - pakiet phonenumbers nie radzi sobie z niektórymi formatami numerów),
2. Użyć jakiejś technologii (np. selenium) do wyrenderowania tej części stron, za które odpowiedzialny jest JavaScript (aby trochę to naśladować moje rozwiązanie szuka numerów nie tylko w tekście strony, ale też w skryptach), 
3. Pobierać linki również ze skryptów JavaScript (np. z instrukcji takich jak window.location.href="www.example.com")
