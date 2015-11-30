# Secret-Formula
Orbital 2015 Project

README

**General**

Project Name: Secret Formula

Project URL: [http://secret-formula.appspot.com/](http://secret-formula.appspot.com/)

Goal: Our project aims to bring back the utility of online forms to high school students, after the practice of using them was discontinued due to the Personal Data Protection Act(PDPA) by creating a form creation service that complies with the PDPA.

Our Ignition Slide/Presentation: [https://youtu.be/osQjStOAci0?t=30m44s](https://youtu.be/osQjStOAci0?t=30m44s)

Project Description(Milestone 2 video): [https://www.youtube.com/watch?v=VvzLqOnxJts](https://www.youtube.com/watch?v=VvzLqOnxJts)

App Demonstration(Milestone 3 video): [https://youtu.](https://youtu.be/jHdPO0T7GpE) [be/jHdPO0T7GpE](https://youtu.be/jHdPO0T7GpE)

**Description**

Secret Formula is your regular form creation service, except it's legal. Since the Personal Data Protection Act was implemented in Singapore, other form creation services are unusable in the context of a school because they simply do not protect the personal data from the creators of these services. That's where Secret Formula is different. Using the principle of Symmetric Key Encryption, users of our app will be able to communicate their personal particulars via forms without us, the service providers, being able to access our data. This is also great for people concerned about privacy in other countries.

The way it works is that the form manager creates a form and sends a link to the respondents along with a key. Since this key is communicated between the form manager and the respondent via there own means of communication, there is no way for us to have access to this key. The respondents then use this key to encrypt their data when they fill the form and send it over to the form manager. In order to read the data, the form manager also has to use that same key (hence, Symmetric Key Encryption) to decrypt the results.

We have used AES encryption together with Cipher Block Chaining, which are very trusted techniques in order to ensure maximum security. As our whole project will be open source the transparency will ensure that it works as intended. In the event that our current implementation is not trusted we can make changes to have our users carry out the encryption and decryption on their computers locally instead of on the internet where we can be suspected to be stealing their keys.

**Implemented User Stories**

As a user I want to be able to log in and view my forms and responses to them.

As a user I want to be able to create a form and send the link to my respondents to use.

As a user I want to be create forms with text input, check boxes and radio buttons.

As a user I want to be able to delete forms.

As a user I want to be able to edit forms.

As a user I want to not violate PDPA by encrypting my respondent's responses before storing them in the database.

**Testing**

- We have definitely tested the app ourselves in the process of debugging for example
- We have simulated possible scenarios such as collecting details for a CCA Camp
- We have employed dogfooding for example to ask each other questions but also Wei Liang used it to keep track of his Orbital Log
- We have discussed the app with two teachers at our school
- We have planned to use it to handle registration for the Sustainable Development Youth Convention(SDYC) 2016, organised by our school. We have discussed it with the SDYC ExCo and they seem to be quite happy about it. This is in response to the painful process of having to transfer information from emails to excel spreadsheets that was faced this year.


**Resources and References**

[http://www.google.com.sg/forms/about/](http://www.google.com.sg/forms/about/)

[https://www.pdpc.gov.sg/legislation-and-guidelines/overview](https://www.pdpc.gov.sg/legislation-and-guidelines/overview)

[http://bityard.blogspot.sg/2010/01/symmetric-encryption-with-pycrypto-part.html](http://bityard.blogspot.sg/2010/01/symmetric-encryption-with-pycrypto-part.html)

[http://getbootstrap.com/](http://getbootstrap.com/)

[http://www.w3schools.com/](http://www.w3schools.com/)

[http://stackoverflow.com/](http://stackoverflow.com/)

