---
layout: details-blog
published: true
categories: blogg teknik
heading: Mock an autowired bean
authors:
  - annicasunnman
tags:
topstory: true
comments: true
---

Imagine a service implementation having autowired dependencies like:

~~~ java
@Service
@Transactional(rollbackFor=ServiceException.class)
public class ManageDrugServiceImpl implements ManageDrugService {`

  @Autowired
  private DrugPrescriptionManager drugPrescriptionManager;
  @Autowired
  private UserDAO userDao;
  @Autowired
  private DrugDAO drugDao;

  @Override
  public List getNewDrugsForUser() throws ServiceException {...
~~~

To test this above service in isolation and mock each dependency is not hard. Create a setter method for each dependency and mark it as "only used in test" in your service class and then in your test class you create a EasyMock object for each and set them on the service:

~~~ java
DrugPrescriptionManager managerMock = EasyMock.createMock(DrugPrescriptionManager.class);`

List containers = new ArrayList();
EasyMock.expect(managerMock.getDrugPrescriptionContainers("1111111111")).
    andReturn(containers);
EasyMock.replay(managerMock);
manageDrugService.setDrugPrescriptionManager(managerMock);
~~~

It feels like the "slim and slick code" of the annotated `@autowire` is disappearing when you still need to create your setter methods.

I am a fan of writing "IntegrationTest" with junit. It means that I like to test all the way without mocking some of the parts that isn't needed like the database. It might not be the proper way of writing tests, but I like to test the code all the way to see that everything runs smoothly before I deploy it and runs it for real in a test environment. Some of you would probably say that if I write test in perfect isolation it is not needed to write integration tests. But until I am proved that there is a "perfect isolated unit test world" I will continue to write integration test for some parts of my code.

So my problem is now that if I in my above service class would like to mock the first manager but not the dao beans. I will use EasyMock and then combine it with dbunit to create some testdata in the database. The only way I could figure out how to do it is to create setter methods of all injected beans as above and then autowire the real beans into my testclass and then create the mock of the manager and set all on the service:

~~~ java
@ContextConfiguration(locations = { "classpath:/applicationContext-test.xml" })
public class ManageDrugServiceTest extends AbstractTransactionalJUnit4SpringContextTests {`

  private ManageDrugServiceImpl manageDrugService;
  @Autowired
  private UserDAO userDao;
  @Autowired
  private DrugDAO drugDao;

  @Before
  public void setup() {
    manageDrugService = new ManageDrugServiceImpl();
    manageDrugService.setDrugDao(drugDao);
    manageDrugService.setUserDao(userDao);
  }

  @Test
  public void getNewDrugs() throws Exception {
~~~

It's not pretty at all. I tried to configure a application context for the test context, but couldn't figure out how to get it to work to be able to autowire one bean but not the other ones.
