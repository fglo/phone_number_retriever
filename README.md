# Phone Number Retriever

Zastosowane kryterium wyboru podstron do odwiedzenia:
1.	Sprawdzam czy znormalizowany tekst linku jest w arbitralnie określonej liście (lista zawiera słowa typu „kontakt”, „contact”, „firma” itp.) i biorę tylko te, które tam są,
2.	Sortuję pobrane i odfiltrowane linki według kolejności w jakich ich tekst koresponduje z kolejnością słów we wspomnianej wyżej liście (chcę, aby najpierw sprawdzona została strona „kontakt”, a dopiero po niej ewentualnie „o nas”).
 
Zastosowane kryterium oceny „główności” pobranych numerów::
1.	Sprawdzam pobrany razem z telefonem tekst, traktując go jak pewnego rodzaju nagłówek i patrzę, czy nie ma w nim słowa „biuro” lub „recepcja” w różnych językach
2.	Jeśli żadne z tych słów nie zostało znalezione, to pobieram pierwszy ze znalezionych numerów, który jest linią stacjonarną
3.	Jeśli żadna linia stacjonarna nie zostanie znaleziona pobieram pierwszy numer z listy.
 
Co można poprawić:
1.	usprawnić sposób odnajdywania numerów telefonów w zawartości strony – pakiet phonenumbers nie radzi sobie z niektórymi formatami numerów),
2.	użyć jakiejś technologii (np. selenium) do wyrenderowania tej części stron, za które odpowiedzialny jest JavaScript (aby trochę to naśladować moje rozwiązanie szuka numerów nie tylko w tekście strony, ale też w skryptach), 
3.	pobierać linki również ze skryptów JavaScript (np. z instrukcji takich jak window.location.href=”www.example.com”)
