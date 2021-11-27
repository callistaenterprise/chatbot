---
categories: blogg teknik
layout: details-blog
published: true
topstory: true
comments: true
heading: Dynamic Lists with Asynchronous Data Loading in SwiftUI
authors:
  - andersforssell
---

SwiftUI is an exciting new way to create UI on Apples platforms. But it is still a young technology and it can sometimes be hard to find information needed to support the implementation of more advanced use cases.

In porting an app to SwiftUI, I’ve been struggling a bit with the `List` view. `List` is a very powerful container view that makes it incredibly easy to create table style components.

But if you want to up your game by adding more features, such as dynamically loading more rows as the the user scrolls, or fetching data asynchronously, it gets a little trickier.  That’s when you would like to know more about how `List` works its magic behind the scenes - but information is scarce about things like cell reuse, redrawing, handling animations, etc.

After some experimentation (and trial and error), I managed to come up with a list that met some more advanced requirements. I also created a few helper components that I would like to share - in case someone else is looking for similar solutions.

## List Requirements
The requirements for my list are as follows.

1. The list should grow dynamically and batch-wise as the user scrolls
2. The data on each row is fetched from a (possibly) slow data source - must be possible to be performed asynchronously in the background
3. Some row data should be animated in two different situations: a) when data has been fetched and b) whenever a row becomes visible
4. Possibility to reset the list and reload data
5. Smooth scrolling throughout

Below is a simple video that shows an example of how the list should work.

[![Video](/assets/blogg/swiftui/RPReplay_Final1587392731.png)](/assets/blogg/swiftui/RPReplay_Final1587392731.mov " ")

# The Solution

I will now walk you through essential parts of the solution. The complete code is shown at the end of this article and can also be downloaded here: <https://github.com/callistaenterprise/SwiftUIListExample>

We start with some of the plumbing which consists of a few protocols and generic components which may be used as a foundation for any list of this type.

## Data Model

First off is the data model and we begin with the `ListDataItem` protocol which should be adopted by the component representing  row data. It must have an `Int` index which is used to determine when more data needs to be loaded, more on this later.

It also contains a function - `fetchData` - that retrieves data for the row in a second - possibly slower - step.

```swift
/// The data items of the list. Must contain index (row number) as a stored property
protocol ListDataItem {
    var index: Int { get set }
    init(index: Int)

    /// Fetch additional data of the item, possibly asynchronously
    func fetchData()

    /// Has the data been fetched?
    var dataIsFetched: Bool { get }
}
```
Next out is the `ListDataProvider` - a generic class that maintains the actual list of data items, stored in a published property that is used directly by the `List` view.

The method `fetchMoreItemsIfNeeded` is called by the view when a new row is presented. It will check if more items need to be fetched and will also initiate loading of additional data for each row.

The properties `itemBatchCount` and `prefetchMargin` can be used to fine tune the list behaviour.

```swift
/// Generic data provider for the list
class ListDataProvider<Item: ListDataItem>: ObservableObject {
    /// - Parameters:
    ///   - itemBatchCount: Number of items to fetch in each batch. It is recommended to be greater than number of rows displayed.
    ///   - prefetchMargin: How far in advance should the next batch be fetched? Greater number means more eager.
    ///                     Sholuld be less than temBatchSize.
    init(itemBatchCount: Int = 20, prefetchMargin: Int = 3) {
        itemBatchSize = itemBatchCount
        self.prefetchMargin = prefetchMargin
        reset()
    }

    private let itemBatchSize: Int
    private let prefetchMargin: Int

    private(set) var listID: UUID = UUID()

    func reset() {
        list = []
        listID = UUID()
        fetchMoreItemsIfNeeded(currentIndex: -1)
    }

    @Published var list: [Item] = []

    /// Extend the list if we are close to the end, based on the specified index
    func fetchMoreItemsIfNeeded(currentIndex: Int) {
        guard currentIndex >= list.count - prefetchMargin else { return }
        let startIndex = list.count
        for currentIndex in startIndex ..< max(startIndex + itemBatchSize, currentIndex) {
            list.append(Item(index: currentIndex))
            list[currentIndex].fetchData()
        }
    }
}
```

## Views

Now we come to the second part of the plumbing - which concerns the views. The structure is similar  to that of the data model components. There is one protocol - `DynamicListRow` - that the row view should adopt. And a generic struct - `DynamicList` - which is used as the actual list view.

 `DynamicList` may need some further explanation. The generic parameter `Row` is a custom view that is used to visualize the row in any fashion you would like. The list gets it data  from `listProvider`, a property of the type `ListDataProvider` that we defined above.

The `onAppear` modifier on the row view is there to ensure that more items are fetched as needed by calling `fetchMoreItemsIfNeeded` every time a row becomes visible.

There is also an `id` modifier on the list view itself. What is the purpose of that, you may ask? The `listID` property provides a unique id that remains the same until the list is reset, in which case a new unique id is generated. This ensures that list is completely redrawn when it is reset. Leaving it out could sometimes cause the list to not fetch enough data when reset, especially for small batch sizes.

```swift
/// The view for the list row
protocol DynamicListRow: View {
    associatedtype Item: ListDataItem
    var item: Item { get }
    init(item: Item)
}

/// The view for the dynamic list
struct DynamicList<Row: DynamicListRow>: View {
    @ObservedObject var listProvider: ListDataProvider<Row.Item>
    var body: some View {
        return
            List(0 ..< listProvider.list.count, id: \.self) { index in
                Row(item: self.listProvider.list[index])
                    .onAppear {
                        self.listProvider.fetchMoreItemsIfNeeded(currentIndex: index)
                }
            }
            .id(self.listProvider.listID)
    }
}
```

That’s all for the plumbing, let’s move on to an example of how to use this to create our list.

# List Example

Here is an example of how to implement a list using the components we’ve defined above.

To be able to demonstrate how it works with asynchronous data loading we start with a very simple datastore called `SlowDataStore`. It offers a static function that will give us a random amount between 0 and 1 as a publisher which takes between 0.5 and 2.0 seconds to deliver the value - implemented as a `usleep` on a background queue.

```swift
struct SlowDataStore {
    static func getAmount(forIndex _: Int) -> AnyPublisher<Double, Never> {
        Just(Double.random(in: 0 ..< 1))
            .subscribe(on: DispatchQueue.global(qos: .background))
            .map { val in usleep(UInt32.random(in: 500_000 ..< 2_000_000)); return val }
            .eraseToAnyPublisher()
    }
}
```

Next, we create our custom data item in the class `MyDataItem` which conforms to the `ListDataItem` protocol. It is a quite straightforward implementation of the protocol requirements. Note that `dataPublisher` needs to be a stored property in order to keep the publisher from `SlowDataStore` alive while waiting for the data to arrive.


```swift
final class MyDataItem: ListDataItem, ObservableObject {
    init(index: Int) {
        self.index = index
    }

    var dataIsFetched: Bool {
        amount != nil
    }

    var index: Int = 0

    @Published var amount: Double?

    var label: String {
        "Line \(index)"
    }

    private var dataPublisher: AnyCancellable?

    func fetchData() {
        if !dataIsFetched {
            dataPublisher = SlowDataStore.getAmount(forIndex: index)
                .receive(on: DispatchQueue.main)
                .sink { amount in
                    self.amount = amount
            }
        }
    }
}
```

The final part of the list is our custom row view which conforms to the `DynamicListRow` protocol. The row contains a horizontal stack with three elements:
- A text view displaying the line number
- A text view displaying "Loading..." if data is not yet available, otherwise displaying the amount.
- A custom graph bar view that displays the amount graphically. The implementation of `GraphBar` is given with the complete solution at the end.

The animation is triggered by the two modifiers on the horizontal stack. The first one - `onReceive` - is used when data first arrives from the `SlowDataStore`. The second one - `onAppear` - is used when the row appears and data is already available.

> **Note:** The animation triggered by `onReceive` and `onAppear` needs to be mutually exclusive, otherwise the animation will not work correctly. That’s why we test the property `dataIsFetched`.

```swift
struct MyListRow: DynamicListRow {
    init(item: MyDataItem) {
        self.item = item
    }

    @ObservedObject var item: MyDataItem
    @State var animatedAmount: Double?

    let graphAnimation = Animation.interpolatingSpring(stiffness: 30, damping: 8)

    var body: some View {
        HStack {
            Text(self.item.label)
                .frame(width: 60, alignment: .leading)
                .font(.callout)
            Text(self.item.amount == nil ? "Loading..." :
                String(format: "Amount: %.1f", self.item.amount!))
                .frame(width: 100, alignment: .leading)
                .font(.callout)
            GraphBar(amount: self.item.amount, animatedAmount: self.$animatedAmount)
        }
        .onReceive(self.item.$amount) { amount in
            if !self.item.dataIsFetched {
                withAnimation(self.graphAnimation) {
                    self.animatedAmount = amount
                }
            }
        }
        .onAppear {
            if self.item.dataIsFetched {
                withAnimation(self.graphAnimation) {
                    self.animatedAmount = self.item.amount
                }
            }
        }
    }
}
```

We now just need to wrap it all up in a container view as shown below.

```swift
struct ContentView: View {
    var listProvider = ListDataProvider<MyDataItem>(itemBatchCount: 20, prefetchMargin: 3)
    var body: some View {
        VStack {
            DynamicList<MyListRow>(listProvider: listProvider)

            Button("Reset") {
                self.listProvider.reset()
            }
        }
    }
}
```

# Conclusion

I hope this article contains some useful information that will help you build your own lists based on similar requirements. Please let me know what you think, and feel free to post any questions, comments or suggestions.

The complete code is given below. You can also download sample XCode-project here: <https://github.com/callistaenterprise/SwiftUIListExample>

# Complete Source Code
```swift
//
//    DynamicListView.swift
//
//

import Combine
import SwiftUI

// MARK: - General Components

/// The data items of the list. Must contain index (row number) as a stored property.
protocol ListDataItem {
    var index: Int { get set }
    init(index: Int)

    /// Fetch additional data of the item, possibly asynchronously.
    func fetchData()

    /// Has the data been fetched?
    var dataIsFetched: Bool { get }
}

/// Generic data provider for the list.
class ListDataProvider<Item: ListDataItem>: ObservableObject {
    /// - Parameters:
    ///   - itemBatchCount: Number of items to fetch in each batch. It is recommended to be greater than number of rows displayed.
    ///   - prefetchMargin: How far in advance should the next batch be fetched? Greater number means more eager.
    ///                     Sholuld be less than temBatchSize
    init(itemBatchCount: Int = 20, prefetchMargin: Int = 3) {
        itemBatchSize = itemBatchCount
        self.prefetchMargin = prefetchMargin
        reset()
    }

    private let itemBatchSize: Int
    private let prefetchMargin: Int

    private(set) var listID: UUID = UUID()

    func reset() {
        list = []
        listID = UUID()
        fetchMoreItemsIfNeeded(currentIndex: -1)
    }

    @Published var list: [Item] = []

    /// Extend the list if we are close to the end, based on the specified index
    func fetchMoreItemsIfNeeded(currentIndex: Int) {
        guard currentIndex >= list.count - prefetchMargin else { return }
        let startIndex = list.count
        for currentIndex in startIndex ..< max(startIndex + itemBatchSize, currentIndex) {
            list.append(Item(index: currentIndex))
            list[currentIndex].fetchData()
        }
    }
}

/// The view for the list row
protocol DynamicListRow: View {
    associatedtype Item: ListDataItem
    var item: Item { get }
    init(item: Item)
}

/// The view for the dynamic list
struct DynamicList<Row: DynamicListRow>: View {
    @ObservedObject var listProvider: ListDataProvider<Row.Item>
    var body: some View {
        return
            List(0 ..< listProvider.list.count, id: \.self) { index in
                    Row(item: self.listProvider.list[index])
                        .onAppear {
                            self.listProvider.fetchMoreItemsIfNeeded(currentIndex: index)
                        }
                }
                .id(self.listProvider.listID)
    }
}

// MARK: - Dynamic List Example

struct SlowDataStore {
    static func getAmount(forIndex _: Int) -> AnyPublisher<Double, Never> {
        Just(Double.random(in: 0 ..< 1))
            .subscribe(on: DispatchQueue.global(qos: .background))
            .map { val in usleep(UInt32.random(in: 500_000 ..< 2_000_000)); return val }
            .eraseToAnyPublisher()
    }
}

final class MyDataItem: ListDataItem, ObservableObject {
    init(index: Int) {
        self.index = index
    }

    var dataIsFetched: Bool {
        amount != nil
    }

    var index: Int = 0

    @Published var amount: Double?

    var label: String {
        "Line \(index)"
    }

    private var dataPublisher: AnyCancellable?

    func fetchData() {
        if !dataIsFetched {
            dataPublisher = SlowDataStore.getAmount(forIndex: index)
                .receive(on: DispatchQueue.main)
                .sink { amount in
                    self.amount = amount
                }
        }
    }
}

struct MyListRow: DynamicListRow {
    init(item: MyDataItem) {
        self.item = item
    }

    @ObservedObject var item: MyDataItem
    @State var animatedAmount: Double?

    let graphAnimation = Animation.interpolatingSpring(stiffness: 30, damping: 8)

    var body: some View {
        HStack {
            Text(self.item.label)
                .frame(width: 60, alignment: .leading)
                .font(.callout)
            Text(self.item.amount == nil ? "Loading..." :
                String(format: "Amount: %.1f", self.item.amount!))
                .frame(width: 100, alignment: .leading)
                .font(.callout)
            GraphBar(amount: self.item.amount, animatedAmount: self.$animatedAmount)
        }
        .onReceive(self.item.$amount) { amount in
            if !self.item.dataIsFetched {
                withAnimation(self.graphAnimation) {
                    self.animatedAmount = amount
                }
            }
        }
        .onAppear {
            if self.item.dataIsFetched {
                withAnimation(self.graphAnimation) {
                    self.animatedAmount = self.item.amount
                }
            }
        }
    }
}

struct GraphBar: View {
    let amount: Double?
    @Binding var animatedAmount: Double?

    var color: Color {
        guard let theAmount = amount else { return Color.gray }
        switch theAmount {
        case 0.0 ..< 0.3: return Color.red
        case 0.3 ..< 0.7: return Color.yellow
        case 0.7 ... 1.0: return Color.green
        default: return Color.gray
        }
    }

    var body: some View {
        GeometryReader { geometry in
            ZStack {
                Capsule()
                    .frame(maxWidth: CGFloat(geometry.size.width * CGFloat(self.animatedAmount ?? 0)), maxHeight: 20)
                    .foregroundColor(self.color)
            }.frame(width: geometry.size.width, height: geometry.size.height, alignment: .leading)
        }
    }
}

struct ContentView: View {
    var listProvider = ListDataProvider<MyDataItem>(itemBatchCount: 20, prefetchMargin: 3)
    var body: some View {
        VStack {
            DynamicList<MyListRow>(listProvider: listProvider)

            Button("Reset") {
                self.listProvider.reset()
            }
        }
    }
}

struct DynamicList_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
            .environment(\.colorScheme, .dark)
    }
}
```
